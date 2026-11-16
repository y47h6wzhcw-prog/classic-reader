import 'package:flutter/material.dart';

import '../data/book_repository.dart';
import '../data/prefs_store.dart';
import 'reader_page.dart';

/// 书架：分类浏览 + 搜索 + 最近阅读
class ShelfPage extends StatefulWidget {
  const ShelfPage({
    super.key,
    required this.repo,
    required this.store,
    this.onPrefsChanged,
  });

  final BookRepository repo;
  final PrefsStore store;

  /// 外观设置变化时通知上层（用于同步 App 主题）
  final void Function(ReaderPrefs prefs)? onPrefsChanged;

  @override
  State<ShelfPage> createState() => _ShelfPageState();
}

class _ShelfPageState extends State<ShelfPage> {
  Map<int, BookProgress> _progress = {};
  int _tab = 0; // 0=中文 1=英文 2=最近
  String _query = '';
  final TextEditingController _search = TextEditingController();
  late final TabController _tabController;

  @override
  void initState() {
    super.initState();
    _progress = widget.store.loadProgress();
    _tabController = TabController(length: 3, vsync: this);
    _tabController.addListener(() {
      if (!_tabController.indexIsChanging) {
        setState(() => _tab = _tabController.index);
      }
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    _search.dispose();
    super.dispose();
  }

  List<Book> _current() {
    final base = _tab == 0
        ? widget.repo.chinese
        : _tab == 1
            ? widget.repo.english
            : _recentlyRead();
    if (_query.trim().isEmpty) return base;
    final q = _query.trim().toLowerCase();
    return base
        .where((b) =>
            b.title.toLowerCase().contains(q) ||
            b.titleAlt.toLowerCase().contains(q) ||
            b.author.toLowerCase().contains(q))
        .toList();
  }

  List<Book> _recentlyRead() {
    final list = widget.repo.all.where((b) => (_progress[b.id]?.started ?? false)).toList();
    list.sort((a, b) =>
        (_progress[b.id]?.lastRead ?? 0).compareTo(_progress[a.id]?.lastRead ?? 0));
    return list;
  }

  Future<void> _open(Book book) async {
    final store = widget.store;
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ReaderPage(
          book: book,
          repo: widget.repo,
          store: store,
          progress: _progress[book.id] ?? const BookProgress(),
          onProgress: (offset) {
            store.saveProgress(book.id, offset);
            _progress = store.loadProgress();
          },
          onPrefsChanged: widget.onPrefsChanged,
        ),
      ),
    );
    if (mounted) setState(() => _progress = widget.store.loadProgress());
  }

  @override
  Widget build(BuildContext context) {
    final books = _current();
    return Scaffold(
      appBar: AppBar(
        title: const Text('经典书房',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500)),
        backgroundColor: Theme.of(context).colorScheme.surface,
        surfaceTintColor: Colors.transparent,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(96),
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
                child: TextField(
                  controller: _search,
                  onChanged: (v) => setState(() => _query = v),
                  decoration: InputDecoration(
                    hintText: '搜索书名或作者',
                    prefixIcon: const Icon(Icons.search, size: 20),
                    isDense: true,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                      borderSide: BorderSide.none,
                    ),
                    filled: true,
                    fillColor: Theme.of(context).colorScheme.surfaceVariant
                        .withOpacity(.6),
                  ),
                ),
              ),
              TabBar(
                controller: _tabController,
                tabs: const [
                  Tab(text: '中文'),
                  Tab(text: 'English'),
                  Tab(text: '最近阅读'),
                ],
              ),
            ],
          ),
        ),
      ),
      body: books.isEmpty
          ? Center(
              child: Text(
                _tab == 2 ? '还没有阅读记录' : '没有匹配的书',
                style: TextStyle(
                    fontSize: 14, color: Theme.of(context).colorScheme.outline),
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
              itemCount: books.length,
              itemBuilder: (ctx, i) => _BookTile(
                book: books[i],
                progress: _progress[books[i].id],
                onTap: () => _open(books[i]),
              ),
            ),
    );
  }
}

class _BookTile extends StatelessWidget {
  const _BookTile({
    required this.book,
    required this.progress,
    required this.onTap,
  });

  final Book book;
  final BookProgress? progress;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final pct = progress?.started ?? false
        ? ((progress!.offset / (progress!.offset + 1)).clamp(0.0, 1.0))
        : 0.0;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 10),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 46,
              height: 62,
              decoration: BoxDecoration(
                color: book.isChinese
                    ? scheme.secondaryContainer
                    : scheme.primaryContainer,
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: scheme.outlineVariant.withOpacity(.5)),
              ),
              alignment: Alignment.center,
              child: Text(
                book.isChinese ? '中' : 'EN',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                  color: book.isChinese
                      ? scheme.onSecondaryContainer
                      : scheme.onPrimaryContainer,
                ),
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    book.displayTitle,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    book.isChinese
                        ? '${book.author} · ${book.titleAlt}'
                        : '${book.author} · ${book.title}',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(fontSize: 12, color: scheme.outline),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    '${(book.chars / 10000).toStringAsFixed(1)} 万字',
                    style: TextStyle(fontSize: 11, color: scheme.outline),
                  ),
                  if (progress?.started ?? false) ...[
                    const SizedBox(height: 6),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(2),
                      child: LinearProgressIndicator(
                        value: pct == 0 ? 0.02 : pct,
                        minHeight: 2.5,
                        backgroundColor: scheme.outlineVariant.withOpacity(.4),
                      ),
                    ),
                  ],
                ],
              ),
            ),
            Icon(Icons.chevron_right, size: 18, color: scheme.outlineVariant),
          ],
        ),
      ),
    );
  }
}
