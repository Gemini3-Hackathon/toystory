import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/api_client.dart';
import 'providers/auth_provider.dart';
import 'providers/toy_provider.dart';
import 'providers/talk_provider.dart';
import 'screens/my_toys/my_toys_screen.dart';
import 'screens/create_toy/create_toy_screen.dart';
import 'screens/parent/parent_screen.dart';
import 'screens/login/login_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  final apiClient = ApiClient();
  runApp(ToyTalkApp(apiClient: apiClient));
}

class ToyTalkApp extends StatelessWidget {
  final ApiClient apiClient;

  const ToyTalkApp({super.key, required this.apiClient});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider(apiClient)),
        ChangeNotifierProvider(create: (_) => ToyProvider(apiClient)),
        ChangeNotifierProvider(create: (_) => TalkProvider(apiClient)),
      ],
      child: MaterialApp(
        title: 'ToyTalk',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF4DA9E0),
            brightness: Brightness.light,
          ),
          fontFamily: 'Roboto',
          useMaterial3: true,
          scaffoldBackgroundColor: const Color(0xFFFFF8F0),
          appBarTheme: const AppBarTheme(
            backgroundColor: Color(0xFFFFF8F0),
            elevation: 0,
            titleTextStyle: TextStyle(
              color: Color(0xFF4A3728),
              fontSize: 22,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        initialRoute: '/',
        routes: {
          '/': (context) => const MyToysScreen(),
          '/login': (context) => const LoginScreen(),
          '/create': (context) => const CreateToyScreen(),
          '/parent': (context) => const ParentScreen(),
        },
      ),
    );
  }
}
