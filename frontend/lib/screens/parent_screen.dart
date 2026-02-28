import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/toy_provider.dart';
import '../services/api_service.dart';

/// Parent Screen — Conversation logs and summaries
class ParentScreen extends StatefulWidget {
  const ParentScreen({super.key});

  @override
  State<ParentScreen> createState() => _ParentScreenState();
}

class _ParentScreenState extends State<ParentScreen> {
  final _api = ApiService();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('👨‍👩‍👧 부모님 화면'),
      ),
      body: Consumer<ToyProvider>(
        builder: (context, provider, _) {
          if (provider.toys.isEmpty) {
            return const Center(
              child: Text('아직 장난감이 없어요.\n먼저 장난감을 추가해주세요!', textAlign: TextAlign.center),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: provider.toys.length,
            itemBuilder: (context, index) {
              final toy = provider.toys[index];
              return _ToyLogCard(toy: toy, api: _api);
            },
          );
        },
      ),
    );
  }
}

class _ToyLogCard extends StatelessWidget {
  final dynamic toy;
  final ApiService api;

  const _ToyLogCard({required this.toy, required this.api});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ExpansionTile(
        tilePadding: const EdgeInsets.all(16),
        leading: CircleAvatar(
          radius: 28,
          backgroundColor: Theme.of(context).colorScheme.primary,
          backgroundImage: toy.avatarBase64 != null
              ? MemoryImage(base64Decode(toy.avatarBase64!))
              : null,
          child: toy.avatarBase64 == null
              ? Text(toy.name[0], style: const TextStyle(color: Colors.white, fontSize: 20))
              : null,
        ),
        title: Text(toy.name, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(
          toy.personality ?? '대화 기록 보기',
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        children: [
          FutureBuilder<Map<String, dynamic>>(
            future: api.getSummary(toy.id),
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: CircularProgressIndicator()),
                );
              }

              if (snapshot.hasError) {
                return Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(
                    '요약을 불러올 수 없어요',
                    style: TextStyle(color: Colors.grey[500]),
                  ),
                );
              }

              final data = snapshot.data!;
              return Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        _StatChip(
                          icon: Icons.chat_bubble_outline,
                          label: '${data['total_sessions']}회 대화',
                        ),
                        const SizedBox(width: 8),
                        _StatChip(
                          icon: Icons.message,
                          label: '${data['total_messages']}개 메시지',
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    const Text('📋 AI 요약', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.blue[50],
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        data['summary_text'] ?? '요약 없음',
                        style: const TextStyle(fontSize: 14),
                      ),
                    ),
                    const SizedBox(height: 12),
                    // View detailed logs button
                    OutlinedButton.icon(
                      onPressed: () => _showDetailedLogs(context, toy),
                      icon: const Icon(Icons.history),
                      label: const Text('상세 대화 기록 보기'),
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  void _showDetailedLogs(BuildContext context, dynamic toy) async {
    try {
      final logs = await api.getLogs(toy.id);
      if (!context.mounted) return;

      final sessions = logs['sessions'] as List? ?? [];

      showModalBottomSheet(
        context: context,
        isScrollControlled: true,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        builder: (context) => DraggableScrollableSheet(
          initialChildSize: 0.7,
          maxChildSize: 0.95,
          minChildSize: 0.3,
          expand: false,
          builder: (context, scrollController) => Column(
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                child: Text(
                  '${toy.name} 대화 기록',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ),
              Expanded(
                child: sessions.isEmpty
                    ? const Center(child: Text('대화 기록이 없어요'))
                    : ListView.builder(
                        controller: scrollController,
                        itemCount: sessions.length,
                        itemBuilder: (context, i) {
                          final session = sessions[i];
                          final messages = session['messages'] as List? ?? [];
                          return ExpansionTile(
                            title: Text('대화 ${i + 1} (${messages.length}개 메시지)'),
                            subtitle: Text(session['started_at'] ?? ''),
                            children: messages.map<Widget>((msg) {
                              final isChild = msg['role'] == 'child';
                              return ListTile(
                                leading: Icon(
                                  isChild ? Icons.child_care : Icons.smart_toy,
                                  color: isChild ? Colors.blue : Colors.orange,
                                ),
                                title: Text(msg['content'] ?? ''),
                                subtitle: Text(
                                  isChild ? '아이' : toy.name,
                                  style: TextStyle(
                                    color: isChild ? Colors.blue : Colors.orange,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              );
                            }).toList(),
                          );
                        },
                      ),
              ),
            ],
          ),
        ),
      );
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('기록을 불러올 수 없어요: $e')),
        );
      }
    }
  }
}

class _StatChip extends StatelessWidget {
  final IconData icon;
  final String label;

  const _StatChip({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Chip(
      avatar: Icon(icon, size: 16),
      label: Text(label, style: const TextStyle(fontSize: 12)),
      backgroundColor: Colors.grey[100],
    );
  }
}
