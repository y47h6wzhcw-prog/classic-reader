import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// 阅读器外观设置 + 阅读进度，全部存在本地 SharedPreferences（无网络）
class ReaderPrefs {
  ReaderPrefs({
    this.fontSize = 18,
    this.lineHeight = 1.8,
    this.themeMode = ThemeMode.light,
    this.margin = 16,
    this.fontFamily = 'system',
  });

  final double fontSize;
  final double lineHeight;
  final ThemeMode themeMode;
  final double margin;
  final String fontFamily;

  ReaderPrefs copyWith({
    double? fontSize,
    double? lineHeight,
    ThemeMode? themeMode,
    double? margin,
    String? fontFamily,
  }) =>
      ReaderPrefs(
        fontSize: fontSize ?? this.fontSize,
        lineHeight: lineHeight ?? this.lineHeight,
        themeMode: themeMode ?? this.themeMode,
        margin: margin ?? this.margin,
        fontFamily: fontFamily ?? this.fontFamily,
      );

  Map<String, dynamic> toJson() => {
        'fontSize': fontSize,
        'lineHeight': lineHeight,
        'theme': themeMode.name,
        'margin': margin,
        'fontFamily': fontFamily,
      };

  factory ReaderPrefs.fromJson(Map<String, dynamic> j) => ReaderPrefs(
        fontSize: (j['fontSize'] as num?)?.toDouble() ?? 18,
        lineHeight: (j['lineHeight'] as num?)?.toDouble() ?? 1.8,
        themeMode: ThemeMode.values.firstWhere(
          (m) => m.name == j['theme'],
          orElse: () => ThemeMode.light,
        ),
        margin: (j['margin'] as num?)?.toDouble() ?? 16,
        fontFamily: j['fontFamily'] as String? ?? 'system',
      );
}

/// 单本书的阅读状态
class BookProgress {
  const BookProgress({this.bookId = 0, this.offset = 0, this.lastRead = 0});

  final int bookId;
  final int offset; // 字符偏移量
  final int lastRead; // 上次阅读时间戳（毫秒）

  bool get started => offset > 0;

  Map<String, dynamic> toJson() =>
      {'bookId': bookId, 'offset': offset, 'lastRead': lastRead};

  factory BookProgress.fromJson(Map<String, dynamic> j) => BookProgress(
        bookId: j['bookId'] as int? ?? 0,
        offset: j['offset'] as int? ?? 0,
        lastRead: j['lastRead'] as int? ?? 0,
      );
}

/// 本地存储中枢
class PrefsStore {
  static const _kAppearance = 'appearance';
  static const _kProgress = 'progress';

  late final SharedPreferences _sp;

  Future<void> init() async {
    _sp = await SharedPreferences.getInstance();
  }

  // ---------------- 外观 ----------------
  ReaderPrefs loadAppearance() {
    final raw = _sp.getString(_kAppearance);
    if (raw == null) return ReaderPrefs();
    try {
      return ReaderPrefs.fromJson(jsonDecode(raw) as Map<String, dynamic>);
    } catch (_) {
      return ReaderPrefs();
    }
  }

  Future<void> saveAppearance(ReaderPrefs p) async {
    await _sp.setString(_kAppearance, jsonEncode(p.toJson()));
  }

  // ---------------- 进度 ----------------
  Map<int, BookProgress> loadProgress() {
    final raw = _sp.getString(_kProgress);
    if (raw == null) return {};
    try {
      final map = jsonDecode(raw) as Map<String, dynamic>;
      return map.map((k, v) => MapEntry(
            int.parse(k),
            BookProgress.fromJson(v as Map<String, dynamic>),
          ));
    } catch (_) {
      return {};
    }
  }

  Future<void> saveProgress(int bookId, int offset) async {
    final all = loadProgress();
    all[bookId] = BookProgress(
      bookId: bookId,
      offset: offset,
      lastRead: DateTime.now().millisecondsSinceEpoch,
    );
    await _sp.setString(_kProgress, jsonEncode(
      all.map((k, v) => MapEntry(k.toString(), v.toJson())),
    ));
  }

  Future<void> clearProgress(int bookId) async {
    final all = loadProgress()..remove(bookId);
    await _sp.setString(_kProgress, jsonEncode(
      all.map((k, v) => MapEntry(k.toString(), v.toJson())),
    ));
  }
}
