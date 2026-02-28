import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/toy.dart';
import '../../models/message.dart';
import '../../providers/talk_provider.dart';
import '../../services/ws_service.dart';

/// 대화 화면 — 텍스트 입력 + WS 실시간 연동
class TalkScreen extends StatefulWidget {
  final Toy toy;

  const TalkScreen({super.key, required this.toy});

  @override
  State<TalkScreen> createState() => _TalkScreenState();
}

class _TalkScreenState extends State<TalkScreen>
    with TickerProviderStateMixin {
  final _textController = TextEditingController();
  final _scrollController = ScrollController();
  final WsService _wsService = WsService();

  bool _wsConnected = false;
  String? _wsMode;
  bool _isSpeaking = false;
  String? _latestBubbleText;
  late AnimationController _pulseController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    );

    // Clear messages and optionally connect WebSocket
    Future.microtask(() {
      Provider.of<TalkProvider>(context, listen: false).clearMessages();
      _connectWebSocket();
    });
  }

  Future<void> _connectWebSocket() async {
    _wsService.onSessionStarted = (sessionId, mode) {
      setState(() {
        _wsConnected = true;
        _wsMode = mode;
      });
    };

    _wsService.onTranscript = (text) {
      setState(() {
        _latestBubbleText = text;
        _isSpeaking = true;
      });
      // Add to messages list
      final provider = Provider.of<TalkProvider>(context, listen: false);
      provider.addAssistantMessage(text);
      _scrollToBottom();
    };

    _wsService.onTurnComplete = () {
      setState(() => _isSpeaking = false);
      _pulseController.stop();
    };

    _wsService.onError = (msg) {
      debugPrint('WS Error: $msg');
    };

    await _wsService.connect(toyId: widget.toy.toyId);
  }

  @override
  void dispose() {
    _textController.dispose();
    _scrollController.dispose();
    _pulseController.dispose();
    _wsService.disconnect();
    super.dispose();
  }

  void _sendMessage() {
    final text = _textController.text.trim();
    if (text.isEmpty) return;
    _textController.clear();

    final provider = Provider.of<TalkProvider>(context, listen: false);

    if (_wsConnected) {
      // WS 모드: WebSocket으로 전송
      provider.addUserMessage(text);
      _wsService.sendText(text);
      setState(() => _isSpeaking = true);
      _pulseController.repeat(reverse: true);
    } else {
      // HTTP 폴백: API 호출
      provider.sendMessage(widget.toy.toyId, text);
    }
    Future.delayed(const Duration(milliseconds: 100), _scrollToBottom);
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFFF8F0),
      appBar: AppBar(
        title: Row(
          children: [
            // 캐릭터 아바타
            Container(
              width: 40,
              height: 40,
              decoration: const BoxDecoration(
                color: Color(0xFFF9C74F),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.pets, color: Colors.white, size: 24),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(widget.toy.toyName,
                    style: const TextStyle(
                        color: Color(0xFF4A3728), fontWeight: FontWeight.bold, fontSize: 18)),
                Text(
                  _wsConnected
                      ? (_wsMode == 'live' ? '🟢 실시간 연결' : '🟡 텍스트 모드')
                      : '🔴 연결 안됨',
                  style: const TextStyle(fontSize: 11, color: Colors.grey),
                ),
              ],
            ),
          ],
        ),
        backgroundColor: const Color(0xFFFFF8F0),
        elevation: 0,
        iconTheme: const IconThemeData(color: Color(0xFF4A3728)),
      ),
      body: Column(
        children: [
          // 캐릭터 영역 (큰 아이콘 + 말풍선)
          Container(
            padding: const EdgeInsets.symmetric(vertical: 16),
            child: Column(
              children: [
                // 캐릭터 아이콘 (맥동 애니메이션)
                AnimatedBuilder(
                  animation: _pulseController,
                  builder: (context, child) {
                    return Transform.scale(
                      scale: 1.0 + (_isSpeaking ? _pulseController.value * 0.1 : 0),
                      child: Container(
                        width: 120,
                        height: 120,
                        decoration: BoxDecoration(
                          color: const Color(0xFFF9C74F).withAlpha(50),
                          shape: BoxShape.circle,
                          boxShadow: _isSpeaking
                              ? [
                                  BoxShadow(
                                    color: const Color(0xFFF9C74F).withAlpha(100),
                                    blurRadius: 20 + _pulseController.value * 10,
                                    spreadRadius: 5,
                                  ),
                                ]
                              : null,
                        ),
                        child: const Icon(Icons.pets, size: 64, color: Color(0xFFF9844A)),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 12),
                // 말풍선
                if (_latestBubbleText != null)
                  Container(
                    margin: const EdgeInsets.symmetric(horizontal: 32),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withAlpha(13),
                          blurRadius: 8,
                          offset: const Offset(0, 3),
                        ),
                      ],
                    ),
                    child: Text(
                      _latestBubbleText!,
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 16, color: Color(0xFF4A3728)),
                    ),
                  ),
                if (_isSpeaking && _latestBubbleText == null)
                  const Padding(
                    padding: EdgeInsets.all(8.0),
                    child: Text('🤔 생각하고 있어요...',
                        style: TextStyle(fontSize: 14, color: Colors.grey)),
                  ),
              ],
            ),
          ),
          // 대화 기록
          Expanded(
            child: Consumer<TalkProvider>(
              builder: (context, provider, child) {
                WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToBottom());
                if (provider.messages.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text('💬', style: TextStyle(fontSize: 48)),
                        const SizedBox(height: 12),
                        Text(
                          '${widget.toy.toyName}에게 말해보세요!',
                          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold,
                              color: Color(0xFF4A3728)),
                        ),
                      ],
                    ),
                  );
                }

                return ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  itemCount: provider.messages.length,
                  itemBuilder: (context, index) {
                    final msg = provider.messages[index];
                    final isUser = msg.role == 'user';
                    return _ChatBubble(
                      message: msg,
                      isUser: isUser,
                      toyName: widget.toy.toyName,
                    );
                  },
                );
              },
            ),
          ),
          // Loading indicator
          Consumer<TalkProvider>(
            builder: (context, provider, child) {
              if (!provider.loading && !_isSpeaking) {
                return const SizedBox.shrink();
              }
              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                child: Row(
                  children: [
                    Container(
                      width: 28,
                      height: 28,
                      decoration: const BoxDecoration(
                        color: Color(0xFFF9C74F),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.pets, color: Colors.white, size: 16),
                    ),
                    const SizedBox(width: 8),
                    const Text('생각하고 있어요...', style: TextStyle(color: Colors.grey, fontSize: 13)),
                    const SizedBox(width: 8),
                    const SizedBox(width: 14, height: 14,
                        child: CircularProgressIndicator(strokeWidth: 2,
                            color: Color(0xFFF9C74F))),
                  ],
                ),
              );
            },
          ),
          // 입력 영역
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withAlpha(13),
                  blurRadius: 10,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _textController,
                    decoration: InputDecoration(
                      hintText: '${widget.toy.toyName}에게 메시지 보내기...',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                        borderSide: BorderSide.none,
                      ),
                      filled: true,
                      fillColor: const Color(0xFFF5F5F5),
                      contentPadding:
                          const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                    ),
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 8),
                FloatingActionButton.small(
                  onPressed: _sendMessage,
                  backgroundColor: const Color(0xFF4DA9E0),
                  child: const Icon(Icons.send, color: Colors.white),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ChatBubble extends StatelessWidget {
  final Message message;
  final bool isUser;
  final String toyName;

  const _ChatBubble({
    required this.message,
    required this.isUser,
    required this.toyName,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) ...[
            Container(
              width: 32,
              height: 32,
              decoration: const BoxDecoration(
                color: Color(0xFFF9C74F),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.pets, color: Colors.white, size: 18),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: isUser ? const Color(0xFF4DA9E0) : Colors.white,
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(16),
                  topRight: const Radius.circular(16),
                  bottomLeft: Radius.circular(isUser ? 16 : 4),
                  bottomRight: Radius.circular(isUser ? 4 : 16),
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withAlpha(10),
                    blurRadius: 4,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Text(
                message.text,
                style: TextStyle(
                  fontSize: 15,
                  color: isUser ? Colors.white : const Color(0xFF4A3728),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
