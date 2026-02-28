import 'dart:convert';
import 'package:flutter/material.dart';
import '../models/toy.dart';

/// Toy Card Widget — Displays a toy in the grid
class ToyCard extends StatelessWidget {
  final Toy toy;
  final VoidCallback onTap;

  const ToyCard({
    super.key,
    required this.toy,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Card(
        elevation: 4,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Avatar
            Hero(
              tag: 'toy-${toy.id}',
              child: CircleAvatar(
                radius: 50,
                backgroundColor: Theme.of(context).colorScheme.primary.withValues(alpha: 0.2),
                backgroundImage: toy.avatarBase64 != null
                    ? MemoryImage(base64Decode(toy.avatarBase64!))
                    : null,
                child: toy.avatarBase64 == null
                    ? Text(
                        toy.name.isNotEmpty ? toy.name[0] : '?',
                        style: TextStyle(
                          fontSize: 36,
                          fontWeight: FontWeight.bold,
                          color: Theme.of(context).colorScheme.primary,
                        ),
                      )
                    : null,
              ),
            ),
            const SizedBox(height: 12),
            // Name
            Text(
              toy.name,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 4),
            // Tap to talk indicator
            Text(
              '탭해서 대화하기 💬',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey[500],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
