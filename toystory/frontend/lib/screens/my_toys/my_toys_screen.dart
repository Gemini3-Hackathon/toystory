import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/toy_provider.dart';
import '../../models/toy.dart';
import '../talk/talk_screen.dart';

class MyToysScreen extends StatefulWidget {
  const MyToysScreen({super.key});

  @override
  State<MyToysScreen> createState() => _MyToysScreenState();
}

class _MyToysScreenState extends State<MyToysScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() =>
        Provider.of<ToyProvider>(context, listen: false).loadToys());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFFF8F0),
      appBar: AppBar(
        title: const Text(
          '🧸 내 장난감 친구들',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Color(0xFF4A3728),
          ),
        ),
        backgroundColor: const Color(0xFFFFF8F0),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.family_restroom, color: Color(0xFF4DA9E0)),
            onPressed: () => Navigator.pushNamed(context, '/parent'),
          ),
        ],
      ),
      body: Consumer<ToyProvider>(
        builder: (context, provider, child) {
          if (provider.loading) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(color: Color(0xFFF9C74F)),
                  SizedBox(height: 16),
                  Text('장난감 친구들을 불러오고 있어요...', style: TextStyle(fontSize: 16)),
                ],
              ),
            );
          }

          if (provider.toys.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text('🎭', style: TextStyle(fontSize: 80)),
                  const SizedBox(height: 16),
                  const Text(
                    '아직 장난감 친구가 없어요!',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    '아래 버튼을 눌러 새 친구를 만들어보세요 ✨',
                    style: TextStyle(fontSize: 14, color: Colors.grey),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    onPressed: () => Navigator.pushNamed(context, '/create'),
                    icon: const Icon(Icons.add_a_photo),
                    label: const Text('친구 만들기', style: TextStyle(fontSize: 18)),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF4DA9E0),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(24),
                      ),
                    ),
                  ),
                ],
              ),
            );
          }

          return GridView.builder(
            padding: const EdgeInsets.all(16),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              childAspectRatio: 0.8,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
            ),
            itemCount: provider.toys.length,
            itemBuilder: (context, index) {
              final toy = provider.toys[index];
              return _ToyCard(
                toy: toy,
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => TalkScreen(toy: toy),
                  ),
                ),
                onLongPress: () => _showDeleteDialog(context, toy),
              );
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => Navigator.pushNamed(context, '/create'),
        backgroundColor: const Color(0xFFF9844A),
        icon: const Icon(Icons.add_a_photo, color: Colors.white),
        label: const Text('친구 만들기', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
      ),
    );
  }

  void _showDeleteDialog(BuildContext context, Toy toy) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('${toy.toyName}을(를) 삭제할까요?'),
        content: const Text('삭제하면 대화 기록도 함께 사라져요.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('취소'),
          ),
          TextButton(
            onPressed: () {
              Provider.of<ToyProvider>(context, listen: false).deleteToy(toy.toyId);
              Navigator.pop(ctx);
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('삭제'),
          ),
        ],
      ),
    );
  }
}

class _ToyCard extends StatelessWidget {
  final Toy toy;
  final VoidCallback onTap;
  final VoidCallback onLongPress;

  const _ToyCard({
    required this.toy,
    required this.onTap,
    required this.onLongPress,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      onLongPress: onLongPress,
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.08),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: const Color(0xFFF9C74F).withOpacity(0.2),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.pets, size: 50, color: Color(0xFFF9844A)),
            ),
            const SizedBox(height: 12),
            Text(
              toy.toyName,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Color(0xFF4A3728),
              ),
            ),
            if (toy.type != null)
              Text(
                toy.type!,
                style: const TextStyle(fontSize: 12, color: Colors.grey),
              ),
          ],
        ),
      ),
    );
  }
}
