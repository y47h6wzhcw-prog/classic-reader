import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;

/// 一本书的元信息，来自 assets/books/manifest.json
class Book {
  final int id;
  final String lang; // 'zh' | 'en'
  final String file;
  final String title; // 展示用标题（中文书为中文，英文书为英文原名）
  final String titleAlt; // 副标题/别名
  final String author;
  final int chars;

  const Book({
    required this.id,
    required this.lang,
    required this.file,
    required this.title,
    required this.titleAlt,
    required this.author,
    required this.chars,
  });

  factory Book.fromJson(Map<String, dynamic> j) => Book(
        id: j['id'] as int,
        lang: j['lang'] as String,
        file: j['file'] as String,
        title: j['title'] as String,
        titleAlt: j['titleAlt'] as String? ?? '',
        author: j['author'] as String? ?? '',
        chars: j['chars'] as int? ?? 0,
      );

  bool get isChinese => lang == 'zh';

  String get displayTitle => isChinese ? title : titleAlt.isEmpty ? title : titleAlt;
}

/// 书库仓库：一次性载入 manifest，正文按需从 asset 读取并缓存
class BookRepository {
  static const String _manifestPath = 'assets/books/manifest.json';

  List<Book> _all = const [];
  final Map<int, String> _textCache = {};
  bool _loaded = false;

  List<Book> get all => _all;
  List<Book> get chinese => _all.where((b) => b.isChinese).toList();
  List<Book> get english => _all.where((b) => !b.isChinese).toList();

  Future<void> load() async {
    if (_loaded) return;
    final raw = await rootBundle.loadString(_manifestPath);
    final decoded = jsonDecode(raw) as List;
    final list = <Book>[];
    final seen = <int>{};
    for (final e in decoded) {
      final b = Book.fromJson(e as Map<String, dynamic>);
      // 同一 ID 只保留一份（不同版本号指向同一本书时去重）
      if (!seen.add(b.id)) continue;
      list.add(b);
    }
    _all = list;
    _loaded = true;
  }

  Future<String> text(Book book) async {
    final cached = _textCache[book.id];
    if (cached != null) return cached;
    final raw = await rootBundle.loadString('assets/books/${book.file}');
    _textCache[book.id] = raw;
    return raw;
  }
}
