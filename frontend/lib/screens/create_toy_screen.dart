import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../providers/toy_provider.dart';

/// Create Toy Screen — Camera capture + character creation
class CreateToyScreen extends StatefulWidget {
  const CreateToyScreen({super.key});

  @override
  State<CreateToyScreen> createState() => _CreateToyScreenState();
}

class _CreateToyScreenState extends State<CreateToyScreen> with SingleTickerProviderStateMixin {
  final _nameController = TextEditingController();
  String? _photoBase64;
  bool _creating = false;
  String _statusMessage = '';
  late AnimationController _sparkleController;

  @override
  void initState() {
    super.initState();
    _sparkleController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _sparkleController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    final picker = ImagePicker();
    final image = await picker.pickImage(
      source: source,
      maxWidth: 800,
      maxHeight: 800,
      imageQuality: 85,
    );

    if (image != null) {
      final bytes = await image.readAsBytes();
      setState(() {
        _photoBase64 = base64Encode(bytes);
      });
    }
  }

  Future<void> _createToy() async {
    if (_nameController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('장난감 이름을 입력해주세요!')),
      );
      return;
    }

    setState(() {
      _creating = true;
      _statusMessage = '✨ 마법을 부리는 중...';
    });
    _sparkleController.repeat();

    try {
      setState(() => _statusMessage = '📸 장난감 특징을 분석하는 중...');
      await Future.delayed(const Duration(milliseconds: 500));

      setState(() => _statusMessage = '🎨 캐릭터를 만드는 중...');
      
      final toy = await context.read<ToyProvider>().createToy(
        name: _nameController.text.trim(),
        photoBase64: _photoBase64,
      );

      _sparkleController.stop();

      if (mounted) {
        // Show success dialog
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (context) => AlertDialog(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (toy.avatarBase64 != null)
                  CircleAvatar(
                    radius: 60,
                    backgroundImage: MemoryImage(base64Decode(toy.avatarBase64!)),
                  )
                else
                  CircleAvatar(
                    radius: 60,
                    backgroundColor: Theme.of(context).colorScheme.primary,
                    child: Text(
                      toy.name[0],
                      style: const TextStyle(fontSize: 40, color: Colors.white),
                    ),
                  ),
                const SizedBox(height: 16),
                Text(
                  '안녕! 나는 ${toy.name}이야! 🎉',
                  style: Theme.of(context).textTheme.titleLarge,
                  textAlign: TextAlign.center,
                ),
                if (toy.personality != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      toy.personality!,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.grey[600]),
                      textAlign: TextAlign.center,
                    ),
                  ),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop(); // Close dialog
                  Navigator.of(context).pop(); // Go back to MyToys
                },
                child: const Text('내 장난감으로 돌아가기'),
              ),
              ElevatedButton(
                onPressed: () {
                  Navigator.of(context).pop(); // Close dialog
                  Navigator.of(context).pushReplacementNamed(
                    '/talk',
                    arguments: {'toyId': toy.id, 'toyName': toy.name},
                  );
                },
                child: const Text('바로 대화하기!'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('오류가 발생했어요: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _creating = false;
          _statusMessage = '';
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('🎨 새 장난감 만들기')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Photo Section
            GestureDetector(
              onTap: _creating ? null : () => _showImageSourceDialog(),
              child: Container(
                height: 250,
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: _photoBase64 != null
                        ? Theme.of(context).colorScheme.primary
                        : Colors.grey[300]!,
                    width: 2,
                  ),
                ),
                child: _photoBase64 != null
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(18),
                        child: Image.memory(
                          base64Decode(_photoBase64!),
                          fit: BoxFit.cover,
                        ),
                      )
                    : Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.camera_alt, size: 48, color: Colors.grey[400]),
                          const SizedBox(height: 8),
                          Text(
                            '장난감 사진을 찍어주세요!',
                            style: TextStyle(color: Colors.grey[500], fontSize: 16),
                          ),
                        ],
                      ),
              ),
            ),

            const SizedBox(height: 24),

            // Name Input
            TextField(
              controller: _nameController,
              enabled: !_creating,
              decoration: InputDecoration(
                labelText: '장난감 이름',
                hintText: '예: 뽀로로, 테디베어',
                prefixIcon: const Icon(Icons.edit),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                filled: true,
                fillColor: Colors.white,
              ),
              style: const TextStyle(fontSize: 18),
            ),

            const SizedBox(height: 32),

            // Create Button
            if (_creating) ...[
              // Magic Animation
              AnimatedBuilder(
                animation: _sparkleController,
                builder: (context, child) {
                  return Column(
                    children: [
                      SizedBox(
                        height: 60,
                        child: Center(
                          child: CircularProgressIndicator(
                            valueColor: AlwaysStoppedAnimation(
                              Color.lerp(
                                Theme.of(context).colorScheme.primary,
                                Theme.of(context).colorScheme.secondary,
                                _sparkleController.value,
                              )!,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        _statusMessage,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: Theme.of(context).colorScheme.primary,
                        ),
                      ),
                    ],
                  );
                },
              ),
            ] else
              ElevatedButton.icon(
                onPressed: _createToy,
                icon: const Icon(Icons.auto_awesome),
                label: const Text('캐릭터 만들기!', style: TextStyle(fontSize: 18)),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  backgroundColor: Theme.of(context).colorScheme.tertiary,
                  foregroundColor: Colors.white,
                ),
              ),
          ],
        ),
      ),
    );
  }

  void _showImageSourceDialog() {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Wrap(
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt),
              title: const Text('카메라로 찍기'),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.camera);
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text('갤러리에서 선택'),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.gallery);
              },
            ),
          ],
        ),
      ),
    );
  }
}
