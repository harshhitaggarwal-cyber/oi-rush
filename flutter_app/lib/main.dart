import 'dart:convert';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

const apiBaseUrl = String.fromEnvironment('OI_RUSH_API_URL', defaultValue: 'http://localhost:8000');

void main() => runApp(const OIRushApp());
const ink = Color(0xFF07142B), panel = Color(0xFF102342), mint = Color(0xFF00F5C8), blue = Color(0xFF2F78FF);

class OIRushApp extends StatelessWidget {
  const OIRushApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'OI Rush',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(brightness: Brightness.dark, scaffoldBackgroundColor: ink, colorScheme: ColorScheme.fromSeed(seedColor: mint, brightness: Brightness.dark), useMaterial3: true),
    home: const Home(),
  );
}

class Home extends StatelessWidget {
  const Home({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(child: ListView(padding: const EdgeInsets.all(22), children: [
      const SizedBox(height: 28),
      Center(child: Container(width: 84, height: 84, decoration: BoxDecoration(gradient: const LinearGradient(colors: [mint, blue]), borderRadius: BorderRadius.circular(25)), child: const Icon(Icons.bolt_rounded, color: ink, size: 50))),
      const SizedBox(height: 18),
      const Center(child: Text.rich(TextSpan(style: TextStyle(fontSize: 36, fontWeight: FontWeight.w900), children: [TextSpan(text: 'OI ', style: TextStyle(color: Colors.white)), TextSpan(text: 'Rush', style: TextStyle(color: mint))]))),
      const SizedBox(height: 18),
      const Text("Let's enter the world of FnO with an EDGE", textAlign: TextAlign.center, style: TextStyle(fontSize: 25, height: 1.2, fontWeight: FontWeight.w800)),
      const SizedBox(height: 10),
      const Text('NSE options. Clearer analysis.', textAlign: TextAlign.center, style: TextStyle(color: Color(0xFF9FB2D0))),
      const SizedBox(height: 34),
      _MarketCard(title: 'NSE', subtitle: 'Indices & Stocks', detail: 'OPTION CHAIN ANALYSIS', color: blue, icon: Icons.candlestick_chart_rounded, onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const Analysis()))),
      const SizedBox(height: 28),
      const Center(child: Text('NSE ONLY · LIVE DATA NOT CONNECTED', style: TextStyle(color: Color(0xFF7F91AF), fontSize: 11, letterSpacing: 1.1))),
    ])),
  );
}

class _MarketCard extends StatelessWidget {
  const _MarketCard({required this.title, required this.subtitle, required this.detail, required this.color, required this.icon, required this.onTap});
  final String title, subtitle, detail; final Color color; final IconData icon; final VoidCallback onTap;
  @override
  Widget build(BuildContext context) => Material(color: panel, borderRadius: BorderRadius.circular(24), child: InkWell(onTap: onTap, borderRadius: BorderRadius.circular(24), child: Container(padding: const EdgeInsets.all(20), decoration: BoxDecoration(borderRadius: BorderRadius.circular(24), border: Border.all(color: color)), child: Row(children: [Container(width: 58, height: 58, decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(18)), child: Icon(icon, size: 32, color: Colors.white)), const SizedBox(width: 16), Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(title, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800)), const SizedBox(height: 4), Text(subtitle, style: const TextStyle(color: Color(0xFFC2D0E5))), const SizedBox(height: 8), Text(detail, style: const TextStyle(color: mint, fontSize: 9, letterSpacing: .5, fontWeight: FontWeight.w700))])), const Icon(Icons.arrow_forward_rounded, color: mint)]))));
}

class Analysis extends StatefulWidget {
  const Analysis({super.key});
  @override State<Analysis> createState() => _AnalysisState();
}

class _AnalysisState extends State<Analysis> {
  String? underlying = 'NIFTY';
  String expiry = 'Select expiry';
  final instruments = const ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'Select stock'];
  final expiries = const ['Select expiry', 'Nearest available expiry', 'Next available expiry'];

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('OI Rush · NSE'), actions: [IconButton(tooltip: 'Upload NSE CSV', icon: const Icon(Icons.upload_file_rounded), onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const CsvUploadScreen()))) ]),
    body: ListView(padding: const EdgeInsets.all(18), children: [
      const Text('NSE Options', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800)),
      const SizedBox(height: 8),
      const Text('Instrument and expiry selectors will use the official contract master when a permitted data feed is connected.', style: TextStyle(color: Color(0xFF9FB2D0))),
      const SizedBox(height: 20),
      DropdownButtonFormField<String>(value: underlying, decoration: const InputDecoration(labelText: 'Underlying / Stock', border: OutlineInputBorder()), items: instruments.map((x) => DropdownMenuItem(value: x, child: Text(x))).toList(), onChanged: (v) => setState(() => underlying = v)),
      const SizedBox(height: 14),
      DropdownButtonFormField<String>(value: expiry, decoration: const InputDecoration(labelText: 'Expiry', border: OutlineInputBorder()), items: expiries.map((x) => DropdownMenuItem(value: x, child: Text(x))).toList(), onChanged: (v) => setState(() => expiry = v ?? expiry)),
      const SizedBox(height: 20),
      Container(padding: const EdgeInsets.all(14), decoration: BoxDecoration(color: panel, borderRadius: BorderRadius.circular(16)), child: const Row(children: [Icon(Icons.schedule_rounded, color: mint), SizedBox(width: 10), Expanded(child: Text('Snapshot target: 7:30 PM IST · manual CSV upload available'))])),
      const SizedBox(height: 20),
      Container(padding: const EdgeInsets.all(18), decoration: BoxDecoration(color: panel, borderRadius: BorderRadius.circular(18), border: Border.all(color: const Color(0xFF29415F))), child: const Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Icon(Icons.cloud_off_rounded, color: mint, size: 30),
        SizedBox(height: 12),
        Text('Market data unavailable', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800)),
        SizedBox(height: 8),
        Text('A live, authorized NSE data source is not connected yet. No option-chain values or OI signals are displayed until a valid snapshot is available.', style: TextStyle(color: Color(0xFF9FB2D0), height: 1.4)),
      ])),
    ]),
  );
}


class CsvUploadScreen extends StatefulWidget {
  const CsvUploadScreen({super.key});
  @override
  State<CsvUploadScreen> createState() => _CsvUploadScreenState();
}

class _CsvUploadScreenState extends State<CsvUploadScreen> {
  final _formKey = GlobalKey<FormState>();
  final _symbol = TextEditingController(text: 'NIFTY');
  final _expiry = TextEditingController();
  final _sessionDate = TextEditingController();
  final _sourceTimestamp = TextEditingController();
  final _underlyingPrice = TextEditingController();
  final _token = TextEditingController();
  PlatformFile? _file;
  bool _uploading = false;
  String? _message;
  bool _success = false;
  Map<String, dynamic>? _snapshot;

  @override
  void dispose() {
    _symbol.dispose();
    _expiry.dispose();
    _sessionDate.dispose();
    _sourceTimestamp.dispose();
    _underlyingPrice.dispose();
    _token.dispose();
    super.dispose();
  }

  Future<void> _chooseFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['csv'],
      withData: true,
    );
    if (result != null && result.files.isNotEmpty) {
      setState(() {
        _file = result.files.single;
        _message = null;
      });
    }
  }

  Future<void> _upload() async {
    if (!_formKey.currentState!.validate()) return;
    if (_file == null || _file!.bytes == null) {
      setState(() { _message = 'Choose the downloaded NSE .csv file first.'; _success = false; });
      return;
    }
    setState(() { _uploading = true; _message = null; });
    try {
      final uri = Uri.parse('${apiBaseUrl.replaceFirst(RegExp(r'/+$'), '')}/v1/admin/upload/nse-csv');
      final request = http.MultipartRequest('POST', uri)
        ..headers['X-Import-Token'] = _token.text.trim()
        ..fields['symbol'] = _symbol.text.trim().toUpperCase()
        ..fields['expiry'] = _expiry.text.trim()
        ..fields['session_date'] = _sessionDate.text.trim()
        ..fields['source_timestamp'] = _sourceTimestamp.text.trim()
        ..fields['underlying_price'] = _underlyingPrice.text.trim()
        ..files.add(http.MultipartFile.fromBytes('file', _file!.bytes!, filename: _file!.name));
      final streamed = await request.send().timeout(const Duration(seconds: 60));
      final response = await http.Response.fromStream(streamed);
      final decoded = jsonDecode(response.body);
      if (response.statusCode >= 200 && response.statusCode < 300) {
        final chainResponse = await http.get(Uri.parse(
          '${apiBaseUrl.replaceFirst(RegExp(r'/+
        final detail = decoded is Map ? (decoded['detail'] ?? 'Upload failed') : 'Upload failed';
        setState(() { _success = false; _message = '$detail'; });
      }
    } catch (e) {
      setState(() { _success = false; _message = 'Could not reach the OI Rush API. Check API URL and connection. Details: $e'; });
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  InputDecoration _decoration(String label, String hint) => InputDecoration(
    labelText: label, hintText: hint, border: const OutlineInputBorder(),
  );

  String? _required(String? value) => value == null || value.trim().isEmpty ? 'Required' : null;

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Upload NSE CSV')),
    body: Form(
      key: _formKey,
      child: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(color: panel, borderRadius: BorderRadius.circular(16)),
            child: const Text(
              'Download the option-chain CSV manually from NSE, then upload it here. Enter the metadata shown for that same snapshot; do not use the upload time as the source timestamp.',
              style: TextStyle(height: 1.45, color: Color(0xFFC2D0E5)),
            ),
          ),
          const SizedBox(height: 18),
          OutlinedButton.icon(
            onPressed: _uploading ? null : _chooseFile,
            icon: const Icon(Icons.attach_file_rounded),
            label: Text(_file == null ? 'Choose NSE .csv file' : _file!.name),
          ),
          const SizedBox(height: 16),
          TextFormField(controller: _symbol, decoration: _decoration('Underlying symbol', 'NIFTY / BANKNIFTY / RELIANCE'), validator: _required, textCapitalization: TextCapitalization.characters),
          const SizedBox(height: 12),
          TextFormField(controller: _expiry, decoration: _decoration('Expiry date', 'YYYY-MM-DD'), validator: _required),
          const SizedBox(height: 12),
          TextFormField(controller: _sessionDate, decoration: _decoration('Session date', 'YYYY-MM-DD'), validator: _required),
          const SizedBox(height: 12),
          TextFormField(controller: _sourceTimestamp, decoration: _decoration('Actual source timestamp', '2026-10-23T15:30:00+05:30'), validator: _required),
          const SizedBox(height: 12),
          TextFormField(controller: _underlyingPrice, decoration: _decoration('Underlying price', '25450.5'), keyboardType: const TextInputType.numberWithOptions(decimal: true), validator: (v) {
            if (v == null || v.trim().isEmpty) return 'Required';
            if (double.tryParse(v.trim()) == null || double.parse(v.trim()) <= 0) return 'Enter a valid positive price';
            return null;
          }),
          const SizedBox(height: 12),
          TextFormField(controller: _token, decoration: _decoration('Admin import token', 'Configured by the API operator'), obscureText: true, validator: _required),
          const SizedBox(height: 8),
          Text('API: $apiBaseUrl', style: const TextStyle(fontSize: 11, color: Color(0xFF7F91AF))),
          const SizedBox(height: 18),
          FilledButton.icon(
            onPressed: _uploading ? null : _upload,
            icon: _uploading ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.cloud_upload_rounded),
            label: Text(_uploading ? 'Validating and uploading…' : 'Upload and save snapshot'),
          ),
          if (_message != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: panel,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: _success ? mint : Colors.orangeAccent),
              ),
              child: Text(_message!, style: TextStyle(color: _success ? mint : Colors.orangeAccent, height: 1.4)),
            ),
          ],
          if (_snapshot != null && _snapshot!['rows'] is List) ...[
            const SizedBox(height: 24),
            Text('${_snapshot!['underlying']} · ${_snapshot!['expiry']}', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w800)),
            const SizedBox(height: 6),
            Text('Session: ${_snapshot!['session_date']} · Source: ${_snapshot!['source_timestamp']} · Underlying: ${_snapshot!['underlying_price']}', style: const TextStyle(color: Color(0xFF9FB2D0), height: 1.4)),
            const SizedBox(height: 12),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                columns: const [
                  DataColumn(label: Text('Strike')),
                  DataColumn(label: Text('OI PCR')),
                  DataColumn(label: Text('LTP PCR')),
                  DataColumn(label: Text('OI Analysis')),
                ],
                rows: (_snapshot!['rows'] as List).map((item) {
                  final row = item as Map<String, dynamic>;
                  String value(dynamic v) => v == null ? '—' : (v is num ? v.toStringAsFixed(4) : v.toString());
                  return DataRow(cells: [
                    DataCell(Text(value(row['strike']))),
                    DataCell(Text(value(row['oi_pcr']))),
                    DataCell(Text(value(row['ltp_pcr']))),
                    DataCell(Text(row['oi_analysis']?.toString() ?? 'Neutral / No Setup')),
                  ]);
                }).toList(),
              ),
            ),
          ],
          const SizedBox(height: 20),
          const Text('Use only the official NSE CSV export. A successful upload saves a snapshot; it does not enable automatic fetching.', style: TextStyle(color: Color(0xFF9FB2D0), height: 1.4)),
        ],
      ),
    ),
  );
}
), '')}/v1/option-chain/${Uri.encodeComponent(_symbol.text.trim().toUpperCase())}?market=NSE&expiry=${Uri.encodeQueryComponent(_expiry.text.trim())}',
        )).timeout(const Duration(seconds: 30));
        Map<String, dynamic>? snapshot;
        if (chainResponse.statusCode >= 200 && chainResponse.statusCode < 300) {
          snapshot = jsonDecode(chainResponse.body) as Map<String, dynamic>;
        }
        setState(() {
          _success = true;
          _snapshot = snapshot;
          _message = 'Uploaded successfully. ${decoded['row_count']} strikes saved for ${decoded['underlying']} / ${decoded['expiry']}. Source: ${decoded['source_timestamp']}.';
        });
      } else {
        final detail = decoded is Map ? (decoded['detail'] ?? 'Upload failed') : 'Upload failed';
        setState(() { _success = false; _message = '$detail'; });
      }
    } catch (e) {
      setState(() { _success = false; _message = 'Could not reach the OI Rush API. Check API URL and connection. Details: $e'; });
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  InputDecoration _decoration(String label, String hint) => InputDecoration(
    labelText: label, hintText: hint, border: const OutlineInputBorder(),
  );

  String? _required(String? value) => value == null || value.trim().isEmpty ? 'Required' : null;

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Upload NSE CSV')),
    body: Form(
      key: _formKey,
      child: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(color: panel, borderRadius: BorderRadius.circular(16)),
            child: const Text(
              'Download the option-chain CSV manually from NSE, then upload it here. Enter the metadata shown for that same snapshot; do not use the upload time as the source timestamp.',
              style: TextStyle(height: 1.45, color: Color(0xFFC2D0E5)),
            ),
          ),
          const SizedBox(height: 18),
          OutlinedButton.icon(
            onPressed: _uploading ? null : _chooseFile,
            icon: const Icon(Icons.attach_file_rounded),
            label: Text(_file == null ? 'Choose NSE .csv file' : _file!.name),
          ),
          const SizedBox(height: 16),
          TextFormField(controller: _symbol, decoration: _decoration('Underlying symbol', 'NIFTY / BANKNIFTY / RELIANCE'), validator: _required, textCapitalization: TextCapitalization.characters),
          const SizedBox(height: 12),
          TextFormField(controller: _expiry, decoration: _decoration('Expiry date', 'YYYY-MM-DD'), validator: _required),
          const SizedBox(height: 12),
          TextFormField(controller: _sessionDate, decoration: _decoration('Session date', 'YYYY-MM-DD'), validator: _required),
          const SizedBox(height: 12),
          TextFormField(controller: _sourceTimestamp, decoration: _decoration('Actual source timestamp', '2026-10-23T15:30:00+05:30'), validator: _required),
          const SizedBox(height: 12),
          TextFormField(controller: _underlyingPrice, decoration: _decoration('Underlying price', '25450.5'), keyboardType: const TextInputType.numberWithOptions(decimal: true), validator: (v) {
            if (v == null || v.trim().isEmpty) return 'Required';
            if (double.tryParse(v.trim()) == null || double.parse(v.trim()) <= 0) return 'Enter a valid positive price';
            return null;
          }),
          const SizedBox(height: 12),
          TextFormField(controller: _token, decoration: _decoration('Admin import token', 'Configured by the API operator'), obscureText: true, validator: _required),
          const SizedBox(height: 8),
          Text('API: $apiBaseUrl', style: const TextStyle(fontSize: 11, color: Color(0xFF7F91AF))),
          const SizedBox(height: 18),
          FilledButton.icon(
            onPressed: _uploading ? null : _upload,
            icon: _uploading ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.cloud_upload_rounded),
            label: Text(_uploading ? 'Validating and uploading…' : 'Upload and save snapshot'),
          ),
          if (_message != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: panel,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: _success ? mint : Colors.orangeAccent),
              ),
              child: Text(_message!, style: TextStyle(color: _success ? mint : Colors.orangeAccent, height: 1.4)),
            ),
          ],
          const SizedBox(height: 20),
          const Text('Use only the official NSE CSV export. A successful upload saves a snapshot; it does not enable automatic fetching.', style: TextStyle(color: Color(0xFF9FB2D0), height: 1.4)),
        ],
      ),
    ),
  );
}
