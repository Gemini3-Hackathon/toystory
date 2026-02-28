class DailyLog {
  final String date;
  final String toyId;
  final int totalMessages;
  final List<Map<String, dynamic>> conversations;
  final bool isSummarized;

  DailyLog({
    required this.date,
    required this.toyId,
    this.totalMessages = 0,
    this.conversations = const [],
    this.isSummarized = false,
  });

  factory DailyLog.fromJson(Map<String, dynamic> json) {
    return DailyLog(
      date: json['date'] ?? '',
      toyId: json['toyId'] ?? '',
      totalMessages: json['totalMessages'] ?? 0,
      conversations: (json['conversations'] as List?)
          ?.map((c) => Map<String, dynamic>.from(c))
          .toList() ?? [],
      isSummarized: json['isSummarized'] ?? false,
    );
  }
}
