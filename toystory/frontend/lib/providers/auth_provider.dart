import 'package:flutter/material.dart';
import '../services/api_client.dart';
import '../services/auth_service.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _service;
  final ApiClient _api;
  bool _isLoggedIn = false;
  String? _userId;
  String? _nickname;

  AuthProvider(this._api) : _service = AuthService(_api);

  bool get isLoggedIn => _isLoggedIn;
  String? get userId => _userId;
  String? get nickname => _nickname;

  Future<void> checkAuth() async {
    await _api.loadToken();
    // If token exists, consider logged in (simplified for hackathon)
    _isLoggedIn = true;
    notifyListeners();
  }

  Future<bool> login(String email, String password) async {
    try {
      final data = await _service.login(email: email, password: password);
      _isLoggedIn = true;
      _userId = data['user']?['userId'];
      _nickname = data['user']?['nickname'];
      notifyListeners();
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<bool> signup(String email, String password, String nickname) async {
    try {
      await _service.signup(email: email, password: password, nickname: nickname);
      return await login(email, password);
    } catch (e) {
      return false;
    }
  }

  Future<void> logout() async {
    await _service.logout();
    _isLoggedIn = false;
    _userId = null;
    _nickname = null;
    notifyListeners();
  }
}
