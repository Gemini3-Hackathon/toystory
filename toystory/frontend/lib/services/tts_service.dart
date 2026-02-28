import 'dart:typed_data';
import 'package:http/http.dart' as http;

/// TTS 서비스 — 텍스트 → 음성 합성
class TTSService {
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1';

  /// 텍스트를 음성으로 변환 (바이트 반환)
  Future<Uint8List?> synthesize(String text, {String? toyId}) async {
    try {
      final body = {'text': text};
      if (toyId != null) body['toyId'] = toyId;

      final response = await http.post(
        Uri.parse('$baseUrl/tts'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: '{"text": "$text"${toyId != null ? ', "toyId": "$toyId"' : ''}}',
      );

      if (response.statusCode == 200) {
        return response.bodyBytes;
      }
      return null;
    } catch (e) {
      return null;
    }
  }
}
