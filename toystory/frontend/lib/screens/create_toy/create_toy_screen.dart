import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import 'dart:io';
import '../../providers/toy_provider.dart';

class CreateToyScreen extends StatefulWidget {
  const CreateToyScreen({super.key});

  @override
  State<CreateToyScreen> createState() => _CreateToyScreenState();
}

class _CreateToyScreenState extends State<CreateToyScreen>
    with SingleTickerProviderStateMixin {
  final _nameController = TextEditingController();
  final _childNameController = TextEditingController();
  String? _imagePath;
  bool _creating = false;
  late AnimationController _animController;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _childNameController.dispose();
    _animController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    final picker = ImagePicker();
    final image = await picker.pickImage(source: source, maxWidth: 1024);
    if (image != null) {
      setState(() => _imagePath = image.path);
    }
  }

  Future<void> _createToy() async {
    if (_imagePath == null || _nameController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('사진과 이름을 입력해주세요!')),
      );
      return;
    }

    setState(() => _creating = true);
    _animController.repeat();

    final provider = Provider.of<ToyProvider>(context, listen: false);
    final toy = await provider.createToy(
      photoPath: _imagePath!,
      toyName: _nameController.text,
      childName: _childNameController.text,
    );

    _animController.stop();
    setState(() => _creating = false);

    if (toy != null && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('✨ ${toy.toyName} 친구가 태어났어요!')),
      );
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFFF8F0),
      appBar: AppBar(
        title: const Text('✨ 새 친구 만들기',
            style: TextStyle(color: Color(0xFF4A3728), fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFFFFF8F0),
        elevation: 0,
        iconTheme: const IconThemeData(color: Color(0xFF4A3728)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Photo area
            GestureDetector(
              onTap: () => _showImagePicker(),
              child: Container(
                height: 250,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(
                    color: const Color(0xFF4DA9E0).withOpacity(0.3),
                    width: 2,
                  ),
                ),
                child: _imagePath != null
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(22),
                        child: Image.file(File(_imagePath!), fit: BoxFit.cover),
                      )
                    : const Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.camera_alt, size: 64, color: Color(0xFF4DA9E0)),
                          SizedBox(height: 12),
                          Text('장난감 사진을 찍어주세요!',
                              style: TextStyle(fontSize: 18, color: Color(0xFF4DA9E0))),
                          SizedBox(height: 4),
                          Text('탭하여 촬영 또는 갤러리에서 선택',
                              style: TextStyle(fontSize: 12, color: Colors.grey)),
                        ],
                      ),
              ),
            ),
            const SizedBox(height: 24),
            // Name field
            TextField(
              controller: _nameController,
              decoration: InputDecoration(
                labelText: '장난감 이름 (예: 곰돌이)',
                prefixIcon: const Icon(Icons.pets, color: Color(0xFFF9844A)),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
                filled: true,
                fillColor: Colors.white,
              ),
              style: const TextStyle(fontSize: 18),
            ),
            const SizedBox(height: 16),
            // Child name
            TextField(
              controller: _childNameController,
              decoration: InputDecoration(
                labelText: '아이 이름 (선택)',
                prefixIcon: const Icon(Icons.child_care, color: Color(0xFF4DA9E0)),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
                filled: true,
                fillColor: Colors.white,
              ),
            ),
            const SizedBox(height: 32),
            // Create button
            if (_creating)
              Column(
                children: [
                  RotationTransition(
                    turns: _animController,
                    child: const Text('✨', style: TextStyle(fontSize: 48)),
                  ),
                  const SizedBox(height: 16),
                  const Text('마법을 부리고 있어요...',
                      style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold,
                          color: Color(0xFFF9844A))),
                  const SizedBox(height: 8),
                  const LinearProgressIndicator(
                    color: Color(0xFFF9C74F),
                    backgroundColor: Color(0xFFFFF0D0),
                  ),
                ],
              )
            else
              ElevatedButton(
                onPressed: _createToy,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFF9844A),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 18),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(20),
                  ),
                ),
                child: const Text('✨ 마법 시작!',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              ),
          ],
        ),
      ),
    );
  }

  void _showImagePicker() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt, color: Color(0xFF4DA9E0), size: 32),
              title: const Text('카메라로 촬영', style: TextStyle(fontSize: 18)),
              onTap: () {
                Navigator.pop(ctx);
                _pickImage(ImageSource.camera);
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library, color: Color(0xFFF9844A), size: 32),
              title: const Text('갤러리에서 선택', style: TextStyle(fontSize: 18)),
              onTap: () {
                Navigator.pop(ctx);
                _pickImage(ImageSource.gallery);
              },
            ),
          ],
        ),
      ),
    );
  }
}
