class User {
  final String userId;
  final String email;
  final String nickname;
  final String? accessToken;
  final String? refreshToken;

  User({
    required this.userId,
    required this.email,
    required this.nickname,
    this.accessToken,
    this.refreshToken,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      userId: json['userId'] ?? '',
      email: json['email'] ?? '',
      nickname: json['nickname'] ?? '',
    );
  }
}
