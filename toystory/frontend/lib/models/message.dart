class Message {
  final String messageId;
  final String role;
  final String text;
  final String? audioUrl;
  final String? createdAt;

  Message({
    required this.messageId,
    required this.role,
    required this.text,
    this.audioUrl,
    this.createdAt,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      messageId: json['messageId'] ?? '',
      role: json['role'] ?? '',
      text: json['text'] ?? '',
      audioUrl: json['audioUrl'],
      createdAt: json['createdAt'],
    );
  }

  Map<String, dynamic> toJson() => {
    'messageId': messageId,
    'role': role,
    'text': text,
    'audioUrl': audioUrl,
    'createdAt': createdAt,
  };
}
