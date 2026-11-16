import 'package:flutter/material.dart';

import '../data/book_repository.dart';
import '../data/prefs_store.dart';

/// 阅读器：分页式滚动 + 进度记忆 + 设置面板
class ReaderPage extends StatefulWidget {
  const ReaderPage({
    super.key,
    required this.book,
    required this.repo,
    required this.store,
    required this.progress,
    required this.onProgress,
    this.onPrefsChanged,
  });

  final Book book;
  final BookRepository repo;
  final PrefsStore store;
  final BookProgress progress;
  final void Function(int offset) onProgress;

  /// 外观设置变化时通知上层（用于同步 App 主题）
  final void Function(ReaderPrefs prefs)? onPrefsChanged;

  @override
  State<ReaderPage> createState() => _ReaderPageState();
}

class _ReaderPageState extends State<ReaderPage> {
  final ScrollController _scroll = ScrollController();
  final TextEditingController _jump = TextEditingController();

  String _text = '';
  bool _loading = true;
  bool _showToolbar = true;
  late ReaderPrefs _prefs;
  int _chars = 0;

  @override
  void initState() {
    super.initState();
    _prefs = widget.store.loadAppearance();
    _load();
  }

  @override
  void dispose() {
    _scroll.removeListener(_onScroll);
    _scroll.dispose();
    _jump.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    final raw = await widget.repo.text(widget.book);
    if (!mounted) return;
    setState(() {
      _text = raw;
      _chars = raw.length;
      _loading = false;
    });
    // 恢复上次阅读位置
    if (widget.progress.offset > 0) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!_scroll.hasClients) return;
        final target = _offsetToPixel(widget.progress.offset);
        _scroll.jumpTo(target.clamp(0, _scroll.position.maxScrollExtent));
      });
    }
    _scroll.addListener(_onScroll);
  }

  /// 目录跳转：把章节标题的字符偏移换算成像素偏移。
  /// 用 TextPainter 测量标题之前的高度，比按比例估算精确得多。
  double _offsetToPixel(int charOffset) {
    if (!_scroll.hasClients) return 0;
    final cut = charOffset.clamp(0, _text.length);
    // 按 UTF-16 code unit 切，避免引入 characters 依赖
    final text = _text.substring(0, cut);
    final tp = TextPainter(
      text: TextSpan(
        text: text,
        style: TextStyle(
          fontSize: _prefs.fontSize,
          height: _prefs.lineHeight,
          fontFamily: _prefs.fontFamily == 'serif'
              ? 'serif'
              : _prefs.fontFamily == 'mono'
                  ? 'monospace'
                  : null,
        ),
      ),
      textDirection: TextDirection.ltr,
      textScaler: TextScaler.noScaling,
    )..layout(maxWidth: _viewportWidth());
    final target = tp.height - _viewportHeight();
    return target.clamp(0.0, _scroll.position.maxScrollExtent);
  }

  double _viewportWidth() {
    if (!_scroll.hasClients) return 360;
    final w = _scroll.position.viewportDimension;
    return w - _prefs.margin * 2;
  }

  double _viewportHeight() {
    if (!_scroll.hasClients) return 600;
    return _scroll.position.viewportDimension;
  }

  void _onScroll() {
    if (!_scroll.hasClients) return;
    final pos = _scroll.position;
    final ratio = (pos.pixels / (pos.maxScrollExtent == 0 ? 1 : pos.maxScrollExtent))
        .clamp(0.0, 1.0);
    widget.onProgress((ratio * _chars).round());
  }

  /// 点击屏幕中部：切换工具栏
  void _toggleToolbar() {
    setState(() => _showToolbar = !_showToolbar);
  }

  void _apply(ReaderPrefs p) {
    setState(() => _prefs = p);
    widget.store.saveAppearance(p);
    widget.onPrefsChanged?.call(p);
  }

  Future<void> _openSettings() async {
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (ctx) => _SettingsSheet(
        prefs: _prefs,
        onApply: _apply,
      ),
    );
  }

  Future<void> _openToc() async {
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      isScrollControlled: true,
      builder: (ctx) => _TocSheet(
        text: _text,
        onJump: (offset) {
          Navigator.pop(ctx);
          if (!_scroll.hasClients) return;
          final target = _offsetToPixel(offset);
          _scroll.animateTo(target.clamp(0, _scroll.position.maxScrollExtent),
              duration: const Duration(milliseconds: 260));
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = _prefs.themeMode == ThemeMode.dark;
    final bg = isDark ? const Color(0xFF16181C) : const Color(0xFFFAF8F3);
    final fg = isDark ? const Color(0xFFD8D5CE) : const Color(0xFF23201C);

    return Scaffold(
      backgroundColor: bg,
      body: SafeArea(
        child: Column(
          children: [
            AnimatedCrossFade(
              duration: const Duration(milliseconds: 180),
              crossFadeState: _showToolbar
                  ? CrossFadeState.showFirst
                  : CrossFadeState.showSecond,
              firstChild: _buildTopBar(fg, bg),
              secondChild: const SizedBox(width: double.infinity, height: 0),
            ),
            Expanded(
              child: _loading
                  ? const Center(child: CircularProgressIndicator())
                  : GestureDetector(
                      onTap: _toggleToolbar,
                      behavior: HitTestBehavior.translucent,
                      child: SelectionArea(
                        child: SingleChildScrollView(
                          controller: _scroll,
                          padding: EdgeInsets.fromLTRB(
                            _prefs.margin,
                            16,
                            _prefs.margin,
                            120,
                          ),
                          child: Text(
                            _text,
                            style: TextStyle(
                              fontSize: _prefs.fontSize,
                              height: _prefs.lineHeight,
                              color: fg,
                              fontFamily: _prefs.fontFamily == 'serif'
                                  ? 'serif'
                                  : _prefs.fontFamily == 'mono'
                                      ? 'monospace'
                                      : null,
                            ),
                          ),
                        ),
                      ),
                    ),
            ),
            AnimatedCrossFade(
              duration: const Duration(milliseconds: 180),
              crossFadeState: _showToolbar
                  ? CrossFadeState.showFirst
                  : CrossFadeState.showSecond,
              firstChild: _buildBottomBar(fg, bg),
              secondChild: const SizedBox(width: double.infinity, height: 0),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTopBar(Color fg, Color bg) {
    return Container(
      color: bg,
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: Row(
        children: [
          IconButton(
            icon: Icon(Icons.arrow_back, color: fg),
            onPressed: () => Navigator.pop(context),
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.book.displayTitle,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                      fontSize: 15, fontWeight: FontWeight.w500, color: fg),
                ),
                Text(
                  '${widget.book.author} · ${_formatSize(_chars)}',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(fontSize: 12, color: fg.withOpacity(.6)),
                ),
              ],
            ),
          ),
          IconButton(
            icon: Icon(Icons.list, color: fg),
            tooltip: '目录',
            onPressed: _openToc,
          ),
          IconButton(
            icon: Icon(Icons.text_fields, color: fg),
            tooltip: '设置',
            onPressed: _openSettings,
          ),
        ],
      ),
    );
  }

  Widget _buildBottomBar(Color fg, Color bg) {
    final pct = _scroll.hasClients && _scroll.position.maxScrollExtent > 0
        ? (_scroll.position.pixels / _scroll.position.maxScrollExtent)
            .clamp(0.0, 1.0)
        : 0.0;
    return Container(
      color: bg,
      padding: const EdgeInsets.fromLTRB(16, 6, 16, 10),
      child: Column(
        children: [
          Row(
            children: [
              Text('${(pct * 100).toStringAsFixed(1)}%',
                  style: TextStyle(fontSize: 12, color: fg.withOpacity(.6))),
              const SizedBox(width: 12),
              Expanded(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(3),
                  child: LinearProgressIndicator(
                    value: pct,
                    minHeight: 3,
                    backgroundColor: fg.withOpacity(.12),
                    valueColor: AlwaysStoppedAnimation(fg.withOpacity(.55)),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _formatSize(int n) {
    if (n >= 10000) return '${(n / 10000).toStringAsFixed(1)} 万字';
    return '$n 字';
  }
}

/// 目录抽屉：按章节标题（Chapter / 第X回 / 卷X 等）生成
class _TocSheet extends StatefulWidget {
  const _TocSheet({required this.text, required this.onJump});

  final String text;
  final void Function(int charOffset) onJump;

  @override
  State<_TocSheet> createState() => _TocSheetState();
}

class _TocSheetState extends State<_TocSheet> {
  final List<({String title, int offset})> _chapters = [];
  late final TextEditingController _search;

  @override
  void initState() {
    super.initState();
    _search = TextEditingController();
    _buildChapters();
  }

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  void _buildChapters() {
    final lines = widget.text.split('\n');
    var offset = 0;
    final re = RegExp(
      r'^\s*(CHAPTER\s+[IVXLCDM0-9]+|Chapter\s+[IVXLCDM0-9]+|PART\s+[IVXLCDM0-9]+|'
      r'BOOK\s+[IVXLCDM0-9]+|ACT\s+[IVXLCDM0-9]+|SCENE\s+[IVXLCDM0-9]+|'
      r'第[一二三四五六七八九十百千零〇\d]+[回卷部章节幕]|'
      r'卷[一二三四五六七八九十\d]+|'
      r'序[章言]|前言|后记|尾声|楔子)\b',
      caseSensitive: false,
    );
    for (final line in lines) {
      final t = line.trim();
      if (t.isNotEmpty && t.length < 40 && re.hasMatch(t)) {
        _chapters.add((title: t, offset: offset));
      }
      offset += line.length + 1;
    }
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      expand: false,
      initialChildSize: 0.7,
      maxChildSize: 0.92,
      builder: (ctx, ctrl) => Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
            child: Row(
              children: [
                Text('目录',
                    style: Theme.of(ctx)
                        .textTheme
                        .titleMedium
                        ?.copyWith(fontWeight: FontWeight.w500)),
                const Spacer(),
                Text('${_chapters.length} 章',
                    style: Theme.of(ctx).textTheme.bodySmall),
              ],
            ),
          ),
          Expanded(
            child: _chapters.isEmpty
                ? const Center(child: Text('未识别到章节标题'))
                : ListView.builder(
                    controller: ctrl,
                    itemCount: _chapters.length,
                    itemBuilder: (ctx, i) {
                      final c = _chapters[i];
                      return ListTile(
                        dense: true,
                        title: Text(c.title,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(fontSize: 14)),
                        onTap: () => widget.onJump(c.offset),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}

/// 外观设置面板
class _SettingsSheet extends StatefulWidget {
  const _SettingsSheet({required this.prefs, required this.onApply});

  final ReaderPrefs prefs;
  final void Function(ReaderPrefs) onApply;

  @override
  State<_SettingsSheet> createState() => _SettingsSheetState();
}

class _SettingsSheetState extends State<_SettingsSheet> {
  late ReaderPrefs _p = widget.prefs;

  void _update(ReaderPrefs next) {
    setState(() => _p = next);
    widget.onApply(next);
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('阅读设置',
                style: Theme.of(ctx)
                    .textTheme
                    .titleMedium
                    ?.copyWith(fontWeight: FontWeight.w500)),
            const SizedBox(height: 16),
            _row('字号', '${_p.fontSize.round()}'),
            Slider(
              value: _p.fontSize,
              min: 13,
              max: 30,
              divisions: 17,
              onChanged: (v) => _update(_p.copyWith(fontSize: v)),
            ),
            _row('行距', _p.lineHeight.toStringAsFixed(1)),
            Slider(
              value: _p.lineHeight,
              min: 1.3,
              max: 2.6,
              divisions: 13,
              onChanged: (v) => _update(_p.copyWith(lineHeight: v)),
            ),
            _row('页边距', '${_p.margin.round()}'),
            Slider(
              value: _p.margin,
              min: 8,
              max: 48,
              divisions: 10,
              onChanged: (v) => _update(_p.copyWith(margin: v)),
            ),
            const SizedBox(height: 8),
            _row('主题', _p.themeMode == ThemeMode.dark ? '夜间' : '日间'),
            SegmentedButton<ThemeMode>(
              segments: const [
                ButtonSegment(value: ThemeMode.light, label: Text('日间')),
                ButtonSegment(value: ThemeMode.dark, label: Text('夜间')),
              ],
              selected: {_p.themeMode},
              onSelectionChanged: (s) => _update(_p.copyWith(themeMode: s.first)),
            ),
            const SizedBox(height: 16),
            _row('字体', _p.fontFamily),
            SegmentedButton<String>(
              segments: const [
                ButtonSegment(value: 'system', label: Text('系统')),
                ButtonSegment(value: 'serif', label: Text('衬线')),
                ButtonSegment(value: 'mono', label: Text('等宽')),
              ],
              selected: {_p.fontFamily},
              onSelectionChanged: (s) => _update(_p.copyWith(fontFamily: s.first)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _row(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(fontSize: 14)),
        Text(value,
            style: TextStyle(
                fontSize: 13, color: Theme.of(context).colorScheme.outline)),
      ],
    );
  }
}
