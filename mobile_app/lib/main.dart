import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'dart:async';
import 'dart:ui';
import 'core/api_service.dart';
import 'widgets/glass_card.dart';

void main() {
  runApp(const CleanCityApp());
}

class CleanCityApp extends StatelessWidget {
  const CleanCityApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'CleanCity AI',
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: const Color(0xFF2EA043),
        scaffoldBackgroundColor: const Color(0xFF0D1117),
        textTheme: GoogleFonts.outfitTextTheme(ThemeData.dark().textTheme),
      ),
      home: const MainNavigation(),
    );
  }
}

class MainNavigation extends StatefulWidget {
  const MainNavigation({super.key});

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _currentIndex = 0;
  final List<Widget> _pages = [
    const HomeScreen(),
    const ScannerScreen(),
    const MapScreen(),
    const LeaderboardScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBody: true,
      body: _pages[_currentIndex],
      bottomNavigationBar: _buildBottomNav(),
    );
  }

  Widget _buildBottomNav() {
    return Container(
      margin: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22).withOpacity(0.8),
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: Colors.white10),
        boxShadow: const [BoxShadow(color: Colors.black45, blurRadius: 20)],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(30),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: BottomNavigationBar(
            elevation: 0,
            type: BottomNavigationBarType.fixed,
            backgroundColor: Colors.transparent,
            selectedItemColor: const Color(0xFF2EA043),
            unselectedItemColor: Colors.grey,
            currentIndex: _currentIndex,
            onTap: (index) => setState(() => _currentIndex = index),
            items: const [
              BottomNavigationBarItem(icon: Icon(Icons.dashboard_rounded), label: 'Home'),
              BottomNavigationBarItem(icon: Icon(Icons.qr_code_scanner_rounded), label: 'Scan'),
              BottomNavigationBarItem(icon: Icon(Icons.map_rounded), label: 'Map'),
              BottomNavigationBarItem(icon: Icon(Icons.emoji_events_rounded), label: 'Rank'),
            ],
          ),
        ),
      ),
    );
  }
}

// --- SCREENS (MODULAR SECTIONS) ---

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<dynamic> activeBins = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final data = await ApiService.fetchTelemetry();
    setState(() {
      activeBins = data;
      isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(25),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHeader(),
              const SizedBox(height: 30),
              _buildCityPulse(),
              const SizedBox(height: 30),
              const Text('Live Operations', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 15),
              _buildLiveList(),
              const SizedBox(height: 100),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Column(crossAxisAlignment: CrossAxisAlignment.start, children: const [
          Text('CLEANCITY AI', style: TextStyle(color: Color(0xFF2EA043), fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 2)),
          Text('Welcome, Vikram', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900)),
        ]),
        const CircleAvatar(radius: 22, backgroundColor: Color(0xFF161B22), child: Icon(Icons.person, color: Colors.white)),
      ],
    );
  }

  Widget _buildCityPulse() {
    return GlassCard(
      borderColor: const Color(0xFF2EA043).withOpacity(0.3),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: const [
              Text('CITY IMPACT SCORE', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.grey, letterSpacing: 1)),
              Icon(Icons.auto_graph_rounded, color: Color(0xFF2EA043), size: 18),
            ],
          ),
          const SizedBox(height: 10),
          const Text('8,420', style: TextStyle(fontSize: 40, fontWeight: FontWeight.w900)),
          const Text('CO2 REDUCED: 145 KG', style: TextStyle(fontSize: 10, color: Colors.grey)),
        ],
      ),
    );
  }

  Widget _buildLiveList() {
    if (isLoading) return const Center(child: CircularProgressIndicator(color: Color(0xFF2EA043)));
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: activeBins.length > 3 ? 3 : activeBins.length,
      itemBuilder: (context, index) {
        final b = activeBins[index];
        return Container(
          margin: const EdgeInsets.only(bottom: 15),
          padding: const EdgeInsets.all(15),
          decoration: BoxDecoration(color: const Color(0xFF161B22), borderRadius: BorderRadius.circular(20), border: Border.all(color: Colors.white.withOpacity(0.05))),
          child: Row(
            children: [
              Icon(Icons.location_on, color: b['fill_level'] > 80 ? Colors.redAccent : const Color(0xFF2EA043)),
              const SizedBox(width: 15),
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(b['location'], style: const TextStyle(fontWeight: FontWeight.bold)), Text('${b['fill_level']}% Full', style: TextStyle(color: Colors.grey, fontSize: 12))])),
              const Icon(Icons.chevron_right, color: Colors.grey),
            ],
          ),
        );
      },
    );
  }
}

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> {
  bool isScanning = false;
  Map<String, dynamic>? result;

  Future<void> _startScan() async {
    setState(() => isScanning = true);
    await Future.delayed(const Duration(seconds: 2));
    final res = await ApiService.predictWaste('mock_path');
    setState(() {
      result = res;
      isScanning = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          Container(color: Colors.black, child: const Center(child: Icon(Icons.camera_alt, size: 80, color: Colors.white10))),
          if (result == null) _buildHUD(),
          SafeArea(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildAISyncStatus(),
                if (result != null) _buildResultPanel() else _buildScanTrigger(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHUD() {
    return Center(
      child: Container(
        width: 280, height: 280,
        decoration: BoxDecoration(border: Border.all(color: const Color(0xFF2EA043).withOpacity(0.3), width: 2), borderRadius: BorderRadius.circular(40)),
        child: isScanning ? const Center(child: CircularProgressIndicator(color: Color(0xFF2EA043))) : null,
      ),
    );
  }

  Widget _buildAISyncStatus() {
    return Container(margin: const EdgeInsets.all(20), padding: const EdgeInsets.all(15), decoration: BoxDecoration(color: Colors.black54, borderRadius: BorderRadius.circular(15)), child: const Text('AI CORE: READY', style: TextStyle(color: Color(0xFF2EA043), fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 2)));
  }

  Widget _buildScanTrigger() {
    return Padding(
      padding: const EdgeInsets.only(bottom: 120),
      child: GestureDetector(
        onTap: _startScan,
        child: Container(height: 80, width: 80, decoration: BoxDecoration(shape: BoxShape.circle, color: const Color(0xFF2EA043), border: Border.all(color: Colors.white30, width: 4)), child: const Icon(Icons.qr_code_scanner, color: Colors.white, size: 35)),
      ),
    );
  }

  Widget _buildResultPanel() {
    return GlassCard(
      borderColor: const Color(0xFF2EA043),
      child: Column(
        children: [
          Text(result!['label'], style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: Color(0xFF2EA043))),
          const SizedBox(height: 10),
          Text(result!['guidance'], style: const TextStyle(color: Colors.grey)),
          const SizedBox(height: 20),
          Row(children: [
            Expanded(child: ElevatedButton(onPressed: () => setState(() => result = null), style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF2EA043)), child: const Text('DISPOSE'))),
          ]),
        ],
      ),
    );
  }
}

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  LatLng userLoc = const LatLng(23.24, 77.44);
  List<dynamic> bins = [];

  @override
  void initState() {
    super.initState();
    _loadBins();
  }

  Future<void> _loadBins() async {
    final data = await ApiService.fetchTelemetry();
    setState(() => bins = data);
  }

  @override
  Widget build(BuildContext context) {
    return FlutterMap(
      options: MapOptions(initialCenter: userLoc, initialZoom: 13),
      children: [
        TileLayer(urlTemplate: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', subdomains: const ['a', 'b', 'c']),
        MarkerLayer(markers: [
          Marker(point: userLoc, child: const Icon(Icons.my_location, color: Colors.blue, size: 30)),
          ...bins.map((b) => Marker(point: LatLng(b['lat'], b['lon']), child: Icon(Icons.location_on, color: b['fill_level'] > 80 ? Colors.red : Colors.green, size: 30))),
        ]),
      ],
    );
  }
}

class LeaderboardScreen extends StatelessWidget {
  const LeaderboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(body: Center(child: Text('Rankings Coming Soon')));
  }
}
