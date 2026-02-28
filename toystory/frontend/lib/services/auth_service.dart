import 'api_client.dart';

class AuthService {
  final ApiClient _api;

  AuthService(this._api);

  Future<Map<String, dynamic>> signup({
    required String email,
    required String password,
    required String nickname,
  }) async {
    final result = await _api.post('/auth/signup', body: {
      'email': email,
      'password': password,
      'nickname': nickname,
    });
    return result['data'];
  }

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final result = await _api.post('/auth/login', body: {
      'email': email,
      'password': password,
    });
    final data = result['data'];
    await _api.saveToken(data['accessToken']);
    return data;
  }

  Future<void> logout() async {
    await _api.clearToken();
  }
}
