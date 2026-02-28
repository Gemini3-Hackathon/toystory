class WeeklySummary {
  final String weekId;
  final String toyId;
  final String summary;
  final List<String> topics;
  final List<String> emotions;
  final List<String> memorableEvents;

  WeeklySummary({
    required this.weekId,
    required this.toyId,
    required this.summary,
    this.topics = const [],
    this.emotions = const [],
    this.memorableEvents = const [],
  });

  factory WeeklySummary.fromJson(Map<String, dynamic> json) {
    return WeeklySummary(
      weekId: json['weekId'] ?? '',
      toyId: json['toyId'] ?? '',
      summary: json['summary'] ?? '',
      topics: List<String>.from(json['topics'] ?? []),
      emotions: List<String>.from(json['emotions'] ?? []),
      memorableEvents: List<String>.from(json['memorableEvents'] ?? []),
    );
  }
}
