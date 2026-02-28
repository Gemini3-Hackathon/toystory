import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import 'screens/my_toys_screen.dart';
import 'screens/create_toy_screen.dart';
import 'screens/talk_screen.dart';
import 'screens/parent_screen.dart';
import 'providers/toy_provider.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ToyProvider()),
      ],
      child: const ToyTalkApp(),
    ),
  );
}

class ToyTalkApp extends StatelessWidget {
  const ToyTalkApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ToyTalk',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF4DA9E0),
          primary: const Color(0xFF4DA9E0),
          secondary: const Color(0xFFF9C74F),
          tertiary: const Color(0xFFF9844A),
          surface: const Color(0xFFF5F5F5),
          error: const Color(0xFFE76F51),
        ),
        textTheme: GoogleFonts.nunitoTextTheme(),
        useMaterial3: true,
        appBarTheme: AppBarTheme(
          backgroundColor: const Color(0xFF4DA9E0),
          foregroundColor: Colors.white,
          titleTextStyle: GoogleFonts.nunito(
            fontSize: 22,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        floatingActionButtonTheme: const FloatingActionButtonThemeData(
          backgroundColor: Color(0xFFF9844A),
          foregroundColor: Colors.white,
        ),
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const MyToysScreen(),
        '/create': (context) => const CreateToyScreen(),
        '/parent': (context) => const ParentScreen(),
      },
      onGenerateRoute: (settings) {
        if (settings.name == '/talk') {
          final args = settings.arguments as Map<String, dynamic>;
          return MaterialPageRoute(
            builder: (context) => TalkScreen(
              toyId: args['toyId'] as String,
              toyName: args['toyName'] as String,
            ),
          );
        }
        return null;
      },
    );
  }
}
