/// Toy Model
class Toy {
  final String id;
  final String name;
  final String? photoPath;
  final String? avatarPath;
  final String? avatarBase64;
  final String? description;
  final String? personality;
  final String? color;
  final String voiceName;
  final String? systemPrompt;
  final String createdAt;

  Toy({
    required this.id,
    required this.name,
    this.photoPath,
    this.avatarPath,
    this.avatarBase64,
    this.description,
    this.personality,
    this.color,
    this.voiceName = 'Puck',
    this.systemPrompt,
    required this.createdAt,
  });

  factory Toy.fromJson(Map<String, dynamic> json) {
    return Toy(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      photoPath: json['photo_path'],
      avatarPath: json['avatar_path'],
      avatarBase64: json['avatar_base64'],
      description: json['description'],
      personality: json['personality'],
      color: json['color'],
      voiceName: json['voice_name'] ?? 'Puck',
      systemPrompt: json['system_prompt'],
      createdAt: json['created_at'] ?? '',
    );
  }
}
