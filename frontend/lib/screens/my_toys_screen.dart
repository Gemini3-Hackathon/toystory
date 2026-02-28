import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/toy_provider.dart';
import '../widgets/toy_card.dart';

/// My Toys Screen — Grid of toy characters
class MyToysScreen extends StatefulWidget {
  const MyToysScreen({super.key});

  @override
  State<MyToysScreen> createState() => _MyToysScreenState();
}

class _MyToysScreenState extends State<MyToysScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      context.read<ToyProvider>().loadToys();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🧸 내 장난감'),
        actions: [
          IconButton(
            icon: const Icon(Icons.family_restroom),
            tooltip: '부모님 화면',
            onPressed: () => Navigator.pushNamed(context, '/parent'),
          ),
        ],
      ),
      body: Consumer<ToyProvider>(
        builder: (context, provider, _) {
          if (provider.loading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (provider.error != null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.cloud_off, size: 64, color: Colors.grey),
                  const SizedBox(height: 16),
                  Text('서버에 연결할 수 없어요', style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 8),
                  ElevatedButton(
                    onPressed: () => provider.loadToys(),
                    child: const Text('다시 시도'),
                  ),
                ],
              ),
            );
          }

          if (provider.toys.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.toys, size: 80, color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.3)),
                  const SizedBox(height: 16),
                  Text(
                    '아직 장난감이 없어요!\n+ 버튼을 눌러 장난감을 추가하세요 🎉',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.grey),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () => provider.loadToys(),
            child: GridView.builder(
              padding: const EdgeInsets.all(16),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 0.85,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
              ),
              itemCount: provider.toys.length,
              itemBuilder: (context, index) {
                return ToyCard(
                  toy: provider.toys[index],
                  onTap: () {
                    Navigator.pushNamed(
                      context,
                      '/talk',
                      arguments: {
                        'toyId': provider.toys[index].id,
                        'toyName': provider.toys[index].name,
                      },
                    );
                  },
                );
              },
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => Navigator.pushNamed(context, '/create'),
        icon: const Icon(Icons.add),
        label: const Text('장난감 추가'),
      ),
    );
  }
}
