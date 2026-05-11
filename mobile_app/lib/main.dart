import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'dart:async';
import 'dart:convert';
import 'dart:ui';
import 'package:http/http.dart' as http;

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
      bottomNavigationBar: Container(
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
                BottomNavigationBarItem(icon: Icon(Icons.dashboard_rounded), label: 'Terminal'),
                BottomNavigationBarItem(icon: Icon(Icons.qr_code_scanner_rounded), label: 'Scanner'),
                BottomNavigationBarItem(icon: Icon(Icons.map_rounded), label: 'City Map'),
                BottomNavigationBarItem(icon: Icon(Icons.emoji_events_rounded), label: 'Rank'),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// --- 1. HOME SCREEN (UPGRADED) ---
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

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
              const SizedBox(height: 35),
              _buildStatusCard(),
              const SizedBox(height: 40),
              const Text('AI Operations', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, letterSpacing: 0.5)),
              const SizedBox(height: 20),
              _buildActionGrid(),
              const SizedBox(height: 30),
              _buildReportingSection(),
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
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('CLEANCITY AI COMMAND', style: TextStyle(color: const Color(0xFF2EA043), letterSpacing: 2, fontSize: 10, fontWeight: FontWeight.bold)),
            const SizedBox(height: 5),
            const Text('Vikram Choure', style: TextStyle(fontSize: 26, fontWeight: FontWeight.w900)),
          ],
        ),
        Container(
          padding: const EdgeInsets.all(2),
          decoration: BoxDecoration(shape: BoxShape.circle, border: Border.all(color: const Color(0xFF2EA043))),
          child: const CircleAvatar(radius: 22, backgroundColor: Colors.transparent, child: Icon(Icons.person_outline, color: Colors.white)),
        ),
      ],
    );
  }

  Widget _buildStatusCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(30),
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [Color(0xFF2EA043), Color(0xFF0D4429)]),
        borderRadius: BorderRadius.circular(30),
        boxShadow: [BoxShadow(color: const Color(0xFF2EA043).withOpacity(0.3), blurRadius: 25, offset: const Offset(0, 15))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('CITY IMPACT SCORE', style: TextStyle(letterSpacing: 1.5, fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white70)),
              Icon(Icons.auto_graph, color: Colors.white70, size: 20),
            ],
          ),
          const SizedBox(height: 15),
          const Text('8,420', style: TextStyle(fontSize: 48, fontWeight: FontWeight.w900)),
          const Text('CO2 REDUCTION: 12.5 kg | Rank: 1st', style: TextStyle(fontSize: 10, color: Colors.white60, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildActionGrid() {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 20,
      mainAxisSpacing: 20,
      childAspectRatio: 1.2,
      children: [
        _buildActionTile(Icons.compost_rounded, 'Bio-Waste', Colors.orange),
        _buildActionTile(Icons.recycling_rounded, 'Recyclables', Colors.blue),
        _buildActionTile(Icons.warning_rounded, 'Hazardous', Colors.red),
        _buildActionTile(Icons.sensors_rounded, 'Sensor Check', const Color(0xFF2EA043)),
      ],
    );
  }

  Widget _buildActionTile(IconData icon, String label, Color color) {
    return Container(
      decoration: BoxDecoration(color: const Color(0xFF161B22), borderRadius: BorderRadius.circular(25), border: Border.all(color: Colors.white.withOpacity(0.05))),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(padding: const EdgeInsets.all(15), decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(20)), child: Icon(icon, color: color, size: 32)),
          const SizedBox(height: 12),
          Text(label, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
        ],
      ),
    );
  }

  Widget _buildReportingSection() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(color: const Color(0xFF161B22), borderRadius: BorderRadius.circular(25), border: Border.all(color: Colors.red.withOpacity(0.1))),
      child: Row(
        children: [
          const Icon(Icons.report_problem_rounded, color: Colors.redAccent, size: 30),
          const SizedBox(width: 20),
          const Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('Emergency Reporting', style: TextStyle(fontWeight: FontWeight.bold)), Text('Found an overflowing bin?', style: TextStyle(color: Colors.grey, fontSize: 12))])),
          Container(padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 8), decoration: BoxDecoration(color: Colors.redAccent.withOpacity(0.1), borderRadius: BorderRadius.circular(10)), child: const Text('REPORT', style: TextStyle(color: Colors.redAccent, fontWeight: FontWeight.bold, fontSize: 12))),
        ],
      ),
    );
  }
}

// --- 2. SCANNER SCREEN (UPGRADED HUD) ---
class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> {
  bool isScanning = true;
  String result = "Scanning...";
  double confidence = 0.0;
  String guidance = "Detecting waste type...";

  @override
  void initState() {
    super.initState();
    _simulateScan();
  }

  void _simulateScan() {
    Timer(const Duration(seconds: 3), () {
      setState(() {
        isScanning = false;
        result = "RECYCLABLE";
        confidence = 0.984;
        guidance = "Disposal: Blue Bin (Dry Waste)";
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          Container(color: Colors.black, child: const Center(child: Icon(Icons.camera_alt, size: 80, color: Colors.white10))),
          _buildHUD(),
          SafeArea(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildAISyncStatus(),
                _buildAnalysisPanel(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHUD() {
    return Center(
      child: SizedBox(
        width: 300, height: 300,
        child: Stack(
          children: [
            Align(alignment: Alignment.topLeft, child: _corner(top: true, left: true)),
            Align(alignment: Alignment.topRight, child: _corner(top: true, left: false)),
            Align(alignment: Alignment.bottomLeft, child: _corner(top: false, left: true)),
            Align(alignment: Alignment.bottomRight, child: _corner(top: false, left: false)),
            if (isScanning)
              TweenAnimationBuilder(
                tween: Tween<double>(begin: 0, end: 300),
                duration: const Duration(seconds: 2),
                builder: (context, double val, child) {
                  return Positioned(top: val, child: Container(width: 300, height: 2, color: const Color(0xFF2EA043).withOpacity(0.5)));
                },
                onEnd: () => setState(() {}),
              ),
          ],
        ),
      ),
    );
  }

  Widget _corner({required bool top, required bool left}) {
    return Container(width: 40, height: 40, decoration: BoxDecoration(border: Border(top: top ? const BorderSide(color: Color(0xFF2EA043), width: 3) : BorderSide.none, bottom: !top ? const BorderSide(color: Color(0xFF2EA043), width: 3) : BorderSide.none, left: left ? const BorderSide(color: Color(0xFF2EA043), width: 3) : BorderSide.none, right: !left ? const BorderSide(color: Color(0xFF2EA043), width: 3) : BorderSide.none)));
  }

  Widget _buildAISyncStatus() {
    return Container(
      margin: const EdgeInsets.all(20),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
      decoration: BoxDecoration(color: const Color(0xFF0D1117).withOpacity(0.8), borderRadius: BorderRadius.circular(20), border: Border.all(color: const Color(0xFF2EA043).withOpacity(0.3))),
      child: Row(
        children: [
          const Icon(Icons.memory, color: Color(0xFF2EA043), size: 20),
          const SizedBox(width: 15),
          const Expanded(child: Text('AI CORE: SYNCHRONIZED', style: TextStyle(color: Color(0xFF2EA043), fontWeight: FontWeight.bold, fontSize: 12))),
          Text('TEMP: 32°C', style: TextStyle(color: Colors.white54, fontSize: 10)),
        ],
      ),
    );
  }

  Widget _buildAnalysisPanel() {
    return Container(
      margin: const EdgeInsets.only(bottom: 120, left: 20, right: 20),
      padding: const EdgeInsets.all(25),
      decoration: BoxDecoration(color: const Color(0xFF161B22), borderRadius: BorderRadius.circular(30), border: Border.all(color: Colors.white10)),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(result, style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 20, color: Color(0xFF2EA043))),
              Text('${(confidence * 100).toStringAsFixed(1)}%', style: const TextStyle(fontWeight: FontWeight.bold)),
            ],
          ),
          const SizedBox(height: 10),
          Text(guidance, style: const TextStyle(color: Colors.grey, fontSize: 14)),
          const SizedBox(height: 25),
          Row(
            children: [
              Expanded(child: _btn('LOG DATA', Colors.blueGrey)),
              const SizedBox(width: 15),
              Expanded(child: _btn('DISPOSE', const Color(0xFF2EA043))),
            ],
          ),
        ],
      ),
    );
  }

  Widget _btn(String txt, Color col) {
    return Container(padding: const EdgeInsets.symmetric(vertical: 15), decoration: BoxDecoration(color: col, borderRadius: BorderRadius.circular(15)), child: Center(child: Text(txt, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12))));
  }
}

// --- 3. MAP SCREEN (INTEGRATED) ---
class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  LatLng driverLocation = const LatLng(23.2500, 77.4400); 
  List<LatLng> routePoints = [];
  String travelTime = "12 min";
  String travelDist = "4.5 km";

  final List<Map<String, dynamic>> bins = [
    {'name': 'Sector 1 (Market)', 'lat': 23.2599, 'lon': 77.4126, 'level': 92},
    {'name': 'BGI Campus', 'lat': 23.2514, 'lon': 77.4815, 'level': 20},
    {'name': 'MP Nagar', 'lat': 23.2333, 'lon': 77.4333, 'level': 88},
  ];

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        FlutterMap(
          options: MapOptions(initialCenter: driverLocation, initialZoom: 13),
          children: [
            TileLayer(
              urlTemplate: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
              subdomains: const ['a', 'b', 'c'],
              tileBuilder: (context, tile, tileImage) {
                return ColorFiltered(colorFilter: const ColorFilter.matrix([-1, 0, 0, 0, 255, 0, -1, 0, 0, 255, 0, 0, -1, 0, 255, 0, 0, 0, 1, 0]), child: tile);
              },
            ),
            MarkerLayer(
              markers: [
                Marker(point: driverLocation, child: const Icon(Icons.local_shipping, color: Colors.blueAccent, size: 40)),
                ...bins.map((b) => Marker(point: LatLng(b['lat'], b['lon']), child: Icon(Icons.location_on, color: b['level'] > 80 ? Colors.redAccent : Colors.greenAccent, size: 35))).toList(),
              ],
            ),
          ],
        ),
        Positioned(
          bottom: 120, left: 20, right: 20,
          child: ClipRRect(
            borderRadius: BorderRadius.circular(25),
            child: BackdropFilter(
              filter: ImageFilter.blur(sigmaX: 15, sigmaY: 15),
              child: Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(color: const Color(0xFF161B22).withOpacity(0.8), border: Border.all(color: Colors.white10)),
                child: Row(
                  children: [
                    const CircleAvatar(backgroundColor: Color(0xFF2EA043), child: Icon(Icons.navigation, color: Colors.white)),
                    const SizedBox(width: 15),
                    const Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('Sector 1 (Market)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)), Text('12 min • 4.5 km', style: TextStyle(color: Colors.grey, fontSize: 12))])),
                    const Text('GO', style: TextStyle(color: Color(0xFF2EA043), fontWeight: FontWeight.w900)),
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

// --- 4. LEADERBOARD SCREEN ---
class LeaderboardScreen extends StatelessWidget {
  const LeaderboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            const Padding(padding: EdgeInsets.all(25), child: Text('CITY ECO-WARRIORS', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900))),
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.all(20),
                itemCount: 10,
                itemBuilder: (context, index) {
                  return Container(
                    margin: const EdgeInsets.only(bottom: 15),
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(color: const Color(0xFF161B22), borderRadius: BorderRadius.circular(25), border: Border.all(color: Colors.white.withOpacity(0.05))),
                    child: Row(
                      children: [
                        Text('#${index+1}', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.grey)),
                        const SizedBox(width: 20),
                        const CircleAvatar(radius: 15, backgroundColor: Color(0xFF2EA043)),
                        const SizedBox(width: 15),
                        Text(index == 0 ? 'Vikram Choure' : 'User ${index+101}', style: const TextStyle(fontWeight: FontWeight.bold)),
                        const Spacer(),
                        Text('${2500 - index*140}', style: const TextStyle(color: Color(0xFF2EA043), fontWeight: FontWeight.w900)),
                      ],
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
