import 'package:flutter/material.dart';
import '../models/message.dart';
import '../services/api_client.dart';
import '../services/talk_service.dart';

class TalkProvider extends ChangeNotifier {
  final TalkService _service;
  List<Message> _messages = [];
  String? _sessionId;
  bool _loading = false;

  TalkProvider(ApiClient api) : _service = TalkService(api);

  List<Message> get messages => _messages;
  String? get sessionId => _sessionId;
  bool get loading => _loading;

  void clearMessages() {
    _messages = [];
    _sessionId = null;
    notifyListeners();
  }

  /// WS 모드용: 사용자 메시지 직접 추가
  void addUserMessage(String text) {
    _messages.add(Message(
      messageId: DateTime.now().millisecondsSinceEpoch.toString(),
      role: 'user',
      text: text,
    ));
    notifyListeners();
  }

  /// WS 모드용: 어시스턴트 메시지 직접 추가
  void addAssistantMessage(String text) {
    _messages.add(Message(
      messageId: 'ws-${DateTime.now().millisecondsSinceEpoch}',
      role: 'assistant',
      text: text,
    ));
    _loading = false;
    notifyListeners();
  }

  /// HTTP 모드: API를 통한 턴제 대화
  Future<void> sendMessage(String toyId, String text) async {
    // 사용자 메시지 즉시 추가
    _messages.add(Message(
      messageId: DateTime.now().millisecondsSinceEpoch.toString(),
      role: 'user',
      text: text,
    ));
    _loading = true;
    notifyListeners();

    try {
      final result = await _service.sendMessage(
        toyId: toyId,
        text: text,
        sessionId: _sessionId,
      );
      _sessionId = result['sessionId'];
      final msgData = result['message'];
      _messages.add(Message.fromJson(msgData));
    } catch (e) {
      _messages.add(Message(
        messageId: 'error-${DateTime.now().millisecondsSinceEpoch}',
        role: 'assistant',
        text: '음... 잘 못 들었어! 다시 말해줄래?',
      ));
    }
    _loading = false;
    notifyListeners();
  }
}
