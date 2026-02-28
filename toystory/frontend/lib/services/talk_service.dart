import 'api_client.dart';

class TalkService {
  final ApiClient _api;

  TalkService(this._api);

  Future<Map<String, dynamic>> sendMessage({
    required String toyId,
    required String text,
    String? sessionId,
  }) async {
    final result = await _api.post('/talk', body: {
      'toyId': toyId,
      'text': text,
      if (sessionId != null) 'sessionId': sessionId,
    });
    return result['data'];
  }
}
