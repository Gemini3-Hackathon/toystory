class Toy {
  final String toyId;
  final String toyName;
  final String? type;
  final String? avatarUrl;
  final Map<String, dynamic>? voiceProfile;
  final String? childName;
  final String? createdAt;

  Toy({
    required this.toyId,
    required this.toyName,
    this.type,
    this.avatarUrl,
    this.voiceProfile,
    this.childName,
    this.createdAt,
  });

  factory Toy.fromJson(Map<String, dynamic> json) {
    return Toy(
      toyId: json['toyId'] ?? '',
      toyName: json['toyName'] ?? '',
      type: json['type'],
      avatarUrl: json['avatarUrl'],
      voiceProfile: json['voiceProfile'] is Map
          ? Map<String, dynamic>.from(json['voiceProfile'])
          : null,
      childName: json['childName'],
      createdAt: json['createdAt'],
    );
  }

  Map<String, dynamic> toJson() => {
    'toyId': toyId,
    'toyName': toyName,
    'type': type,
    'avatarUrl': avatarUrl,
    'voiceProfile': voiceProfile,
    'childName': childName,
    'createdAt': createdAt,
  };
}
