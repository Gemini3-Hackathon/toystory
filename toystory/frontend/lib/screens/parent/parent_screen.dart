import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/toy_provider.dart';
import '../../models/toy.dart';
import '../../services/api_client.dart';
import '../../services/log_service.dart';
import '../../models/daily_log.dart';
import '../../models/weekly_summary.dart';

class ParentScreen extends StatefulWidget {
  const ParentScreen({super.key});

  @override
  State<ParentScreen> createState() => _ParentScreenState();
}

class _ParentScreenState extends State<ParentScreen> {
  late LogService _logService;
  Toy? _selectedToy;
  List<DailyLog> _logs = [];
  List<WeeklySummary> _summaries = [];
  bool _loadingLogs = false;
  bool _loadingSummaries = false;
  int _tabIndex = 0;

  @override
  void initState() {
    super.initState();
    final apiClient = ApiClient();
    _logService = LogService(apiClient);
  }

  Future<void> _loadData(Toy toy) async {
    setState(() {
      _selectedToy = toy;
      _loadingLogs = true;
      _loadingSummaries = true;
    });

    try {
      final logs = await _logService.getLogs(toy.toyId);
      setState(() {
        _logs = logs;
        _loadingLogs = false;
      });
    } catch (e) {
      setState(() => _loadingLogs = false);
    }

    try {
      final summaries = await _logService.getSummary(toy.toyId);
      setState(() {
        _summaries = summaries;
        _loadingSummaries = false;
      });
    } catch (e) {
      setState(() => _loadingSummaries = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      appBar: AppBar(
        title: const Text('👨‍👩‍👧 부모 대시보드',
            style: TextStyle(color: Color(0xFF4A3728), fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Color(0xFF4A3728)),
      ),
      body: Column(
        children: [
          // 장난감 선택
          Container(
            height: 80,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Consumer<ToyProvider>(
              builder: (context, provider, _) {
                if (provider.toys.isEmpty) {
                  return const Center(child: Text('등록된 장난감이 없습니다'));
                }
                return ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: provider.toys.length,
                  itemBuilder: (context, index) {
                    final toy = provider.toys[index];
                    final selected = _selectedToy?.toyId == toy.toyId;
                    return Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 12),
                      child: ChoiceChip(
                        label: Text(toy.toyName),
                        selected: selected,
                        onSelected: (_) => _loadData(toy),
                        selectedColor: const Color(0xFF4DA9E0),
                        labelStyle: TextStyle(
                          color: selected ? Colors.white : const Color(0xFF4A3728),
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          ),
          // 탭
          if (_selectedToy != null)
            Container(
              decoration: const BoxDecoration(
                border: Border(bottom: BorderSide(color: Color(0xFFE0E0E0))),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: GestureDetector(
                      onTap: () => setState(() => _tabIndex = 0),
                      child: Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          border: Border(
                            bottom: BorderSide(
                              color: _tabIndex == 0 ? const Color(0xFF4DA9E0) : Colors.transparent,
                              width: 3,
                            ),
                          ),
                        ),
                        child: Text('📋 대화 기록',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontWeight: _tabIndex == 0 ? FontWeight.bold : FontWeight.normal,
                              color: _tabIndex == 0 ? const Color(0xFF4DA9E0) : Colors.grey,
                            )),
                      ),
                    ),
                  ),
                  Expanded(
                    child: GestureDetector(
                      onTap: () => setState(() => _tabIndex = 1),
                      child: Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          border: Border(
                            bottom: BorderSide(
                              color: _tabIndex == 1 ? const Color(0xFF4DA9E0) : Colors.transparent,
                              width: 3,
                            ),
                          ),
                        ),
                        child: Text('📊 주간 요약',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontWeight: _tabIndex == 1 ? FontWeight.bold : FontWeight.normal,
                              color: _tabIndex == 1 ? const Color(0xFF4DA9E0) : Colors.grey,
                            )),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          // 콘텐츠
          Expanded(
            child: _selectedToy == null
                ? const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.touch_app, size: 64, color: Colors.grey),
                        SizedBox(height: 16),
                        Text('위에서 장난감을 선택해주세요',
                            style: TextStyle(fontSize: 16, color: Colors.grey)),
                      ],
                    ),
                  )
                : _tabIndex == 0
                    ? _buildLogsTab()
                    : _buildSummaryTab(),
          ),
        ],
      ),
    );
  }

  Widget _buildLogsTab() {
    if (_loadingLogs) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFFF9C74F)));
    }
    if (_logs.isEmpty) {
      return const Center(
        child: Text('아직 대화 기록이 없습니다', style: TextStyle(color: Colors.grey)),
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _logs.length,
      itemBuilder: (context, index) {
        final log = _logs[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('📅 ${log.date}',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                    Text('${log.totalMessages}개 메시지',
                        style: const TextStyle(color: Colors.grey)),
                  ],
                ),
                const SizedBox(height: 12),
                ...log.conversations.take(5).map((conv) {
                  final role = conv['role'] == 'user' ? '👶' : '🧸';
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Text('$role ${conv['text']}',
                        style: const TextStyle(fontSize: 14),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis),
                  );
                }),
                if (log.conversations.length > 5)
                  Text('... ${log.conversations.length - 5}개 더',
                      style: const TextStyle(color: Colors.grey, fontSize: 12)),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildSummaryTab() {
    if (_loadingSummaries) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFFF9C74F)));
    }
    if (_summaries.isEmpty) {
      return const Center(
        child: Text('아직 주간 요약이 없습니다', style: TextStyle(color: Colors.grey)),
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _summaries.length,
      itemBuilder: (context, index) {
        final summary = _summaries[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 16),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('📊 ${summary.weekId}',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                const SizedBox(height: 12),
                Text(summary.summary, style: const TextStyle(fontSize: 14)),
                if (summary.topics.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 4,
                    children: summary.topics.map((t) => Chip(
                      label: Text(t, style: const TextStyle(fontSize: 12)),
                      backgroundColor: const Color(0xFFF9C74F).withAlpha(50),
                    )).toList(),
                  ),
                ],
                if (summary.emotions.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Text('감정: ${summary.emotions.join(", ")}',
                      style: const TextStyle(color: Colors.grey, fontSize: 13)),
                ],
              ],
            ),
          ),
        );
      },
    );
  }
}
