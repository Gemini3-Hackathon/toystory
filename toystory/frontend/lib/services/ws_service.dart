import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:web_socket_channel/web_socket_channel.dart';

/// WebSocket 클라이언트 — Live API 실시간 대화 및 턴제 폴백 지원
class WsService {
  static const String _wsBaseUrl = 'ws://10.0.2.2:8000/ws/live';
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  bool _connected = false;
  String? _mode; // 'live' or 'fallback'

  // 콜백
  Function(String text)? onTranscript;
  Function(Uint8List audioData)? onAudioData;
  Function()? onTurnComplete;
  Function()? onInterrupted;
  Function(String message)? onError;
  Function(String sessionId, String mode)? onSessionStarted;

  bool get connected => _connected;
  String? get mode => _mode;

  /// Live API 세션 시작
  Future<void> connect({
    required String toyId,
    String? sessionId,
  }) async {
    try {
      String url = '$_wsBaseUrl?toyId=$toyId';
      if (sessionId != null) {
        url += '&sessionId=$sessionId';
      }

      _channel = WebSocketChannel.connect(Uri.parse(url));
      _connected = true;

      _subscription = _channel!.stream.listen(
        (data) => _handleMessage(data),
        onDone: () {
          _connected = false;
          _mode = null;
        },
        onError: (error) {
          onError?.call('WebSocket 오류: $error');
          _connected = false;
        },
      );
    } catch (e) {
      onError?.call('연결 실패: $e');
      _connected = false;
    }
  }

  void _handleMessage(dynamic data) {
    if (data is Uint8List) {
      // 바이너리 오디오 프레임
      onAudioData?.call(data);
    } else if (data is String) {
      final msg = jsonDecode(data) as Map<String, dynamic>;
      final type = msg['type'] ?? '';

      switch (type) {
        case 'session_started':
          _mode = msg['mode'] ?? 'fallback';
          onSessionStarted?.call(msg['sessionId'] ?? '', _mode!);
          break;
        case 'transcript':
          onTranscript?.call(msg['text'] ?? '');
          break;
        case 'turn_complete':
          onTurnComplete?.call();
          break;
        case 'interrupted':
          onInterrupted?.call();
          break;
        case 'error':
          onError?.call(msg['message'] ?? '알 수 없는 오류');
          break;
        case 'pong':
          break;
        case 'info':
          break;
      }
    }
  }

  /// 텍스트 메시지 전송 (턴제 폴백 모드에서 사용)
  void sendText(String text) {
    if (!_connected || _channel == null) return;
    _channel!.sink.add(jsonEncode({
      'type': 'text',
      'text': text,
    }));
  }

  /// 오디오 프레임 전송 (Live 모드에서 사용)
  void sendAudio(Uint8List audioData) {
    if (!_connected || _channel == null) return;
    _channel!.sink.add(audioData);
  }

  /// 발화 종료 신호
  void sendEndOfTurn() {
    if (!_connected || _channel == null) return;
    _channel!.sink.add(jsonEncode({'type': 'end_of_turn'}));
  }

  /// 바지인 (재생 중단)
  void sendInterrupt() {
    if (!_connected || _channel == null) return;
    _channel!.sink.add(jsonEncode({'type': 'interrupt'}));
  }

  /// 핑
  void sendPing() {
    if (!_connected || _channel == null) return;
    _channel!.sink.add(jsonEncode({'type': 'ping'}));
  }

  /// 연결 종료
  Future<void> disconnect() async {
    _connected = false;
    _mode = null;
    await _subscription?.cancel();
    _subscription = null;
    await _channel?.sink.close();
    _channel = null;
  }
}
