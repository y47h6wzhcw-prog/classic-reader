import 'package:flutter/material.dart';

import 'data/book_repository.dart';
import 'data/prefs_store.dart';
import 'pages/shelf_page.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final store = PrefsStore();
  await store.init();
  final repo = BookRepository();
  await repo.load();
  runApp(ClassicReaderApp(store: store, repo: repo));
}

class ClassicReaderApp extends StatefulWidget {
  const ClassicReaderApp({super.key, required this.store, required this.repo});

  final PrefsStore store;
  final BookRepository repo;

  @override
  State<ClassicReaderApp> createState() => _ClassicReaderAppState();
}

class _ClassicReaderAppState extends State<ClassicReaderApp> {
  ReaderPrefs _prefs = const ReaderPrefs();

  @override
  void initState() {
    super.initState();
    _prefs = widget.store.loadAppearance();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '经典书房',
      debugShowCheckedModeBanner: false,
      themeMode: _prefs.themeMode,
      theme: _buildTheme(Brightness.light),
      darkTheme: _buildTheme(Brightness.dark),
      home: ShelfPage(
        store: widget.store,
        repo: widget.repo,
        onPrefsChanged: (p) => setState(() => _prefs = p),
      ),
    );
  }

  ThemeData _buildTheme(Brightness b) {
    final scheme = ColorScheme.fromSeed(
      seedColor: const Color(0xFF8C6A4A),
      brightness: b,
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor:
          b == Brightness.light ? const Color(0xFFFAF8F3) : const Color(0xFF16181C),
      appBarTheme: AppBarTheme(
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.w500,
          color: b == Brightness.light ? const Color(0xFF23201C) : const Color(0xFFD8D5CE),
        ),
      ),
    );
  }
}
