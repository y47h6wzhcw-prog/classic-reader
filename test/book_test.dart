import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:classic_reader/data/book_repository.dart';
import 'package:classic_reader/data/prefs_store.dart';

void main() {
  test('Book 模型解析正确', () {
    final b = Book.fromJson(const {
      'id': 1342,
      'lang': 'en',
      'file': 'en_1342_x.txt',
      'title': 'Pride and Prejudice',
      'titleAlt': 'Pride and Prejudice',
      'author': 'Jane Austen',
      'chars': 430000,
    });
    expect(b.id, 1342);
    expect(b.isChinese, isFalse);
    expect(b.displayTitle, 'Pride and Prejudice');
  });

  test('中文书 displayTitle 取中文标题', () {
    final b = Book.fromJson(const {
      'id': 24264,
      'lang': 'zh',
      'file': 'zh_24264_x.txt',
      'title': '红楼梦',
      'titleAlt': 'Dream of the Red Chamber',
      'author': '曹雪芹',
      'chars': 900000,
    });
    expect(b.isChinese, isTrue);
    expect(b.displayTitle, '红楼梦');
  });

  test('ReaderPrefs 序列化往返一致', () {
    const p = ReaderPrefs(
      fontSize: 22,
      lineHeight: 2.0,
      themeMode: ThemeMode.dark,
      margin: 24,
      fontFamily: 'serif',
    );
    final restored = ReaderPrefs.fromJson(p.toJson());
    expect(restored.fontSize, 22);
    expect(restored.lineHeight, 2.0);
    expect(restored.themeMode, ThemeMode.dark);
    expect(restored.margin, 24);
    expect(restored.fontFamily, 'serif');
  });

  test('BookProgress 序列化往返一致', () {
    const p = BookProgress(bookId: 42, offset: 1234, lastRead: 999);
    final r = BookProgress.fromJson(p.toJson());
    expect(r.bookId, 42);
    expect(r.offset, 1234);
    expect(r.started, isTrue);
  });
}
