import 'package:flutter/material.dart';
import 'dart:ui';

class GlassCard extends StatelessWidget {
  final Widget child;
  final Color? borderColor;
  final double blur;

  const GlassCard({super.key, required this.child, this.borderColor, this.blur = 15});

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(25),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: blur, sigmaY: blur),
        child: Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22).withOpacity(0.7),
            borderRadius: BorderRadius.circular(25),
            border: Border.all(color: borderColor ?? Colors.white10),
          ),
          child: child,
        ),
      ),
    );
  }
}
