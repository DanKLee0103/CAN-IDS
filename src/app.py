from flask import Flask, render_template, Response, request
from can_ids.detector import Detector
from can_ids.extract import get_mean_intervals, get_baseline_slopes
from can_ids.loader import loader

import csv
import json
import time

app = Flask(__name__)

print("Loading baseline data...")
mean_intervals = get_mean_intervals("../otids_dataset/attack_free.csv")
baseline_slopes = get_baseline_slopes("../otids_dataset/attack_free.csv", mean_intervals)
print("Baseline ready.")

@app.route('/')
def index():
    return render_template('index.html')

filepaths = [
    "../otids_dataset/attack_free.csv" # target == 0
    # "../otids_dataset/DoS_flood.csv", # target == 1
    # "../otids_dataset/Fuzzy_spoof_payload.csv", # target == 2
    # "../otids_dataset/Impersonation_spoof.csv"  # target == 3
]

valid_ids = [int(x, 16) for x in
            ['04f2', '0545', '0164', '04b1', '0153', '02a0', '0382',
             '0018', '0510', '0587', '05e4', '0044', '0316', '0220',
             '05a2', '05f0', '00a1', '0690', '0260', '04f0', '0034',
             '02c0', '01f1', '0081', '05a0', '0043', '051a', '018f',
             '04b0', '0080', '0042', '02b0', '04f1', '0350', '043f',
             '0120', '0165', '00a0', '0050', '059b', '0370', '0110',
             '0517', '0440', '0329']]

@app.route('/stream')
def stream():
    dataset = request.args.get('dataset', 'attack_free')
    warmup = int(request.args.get('warmup', 20000))
    flood_threshold = int(request.args.get('flood_threshold', 125))
    cs_range = float(request.args.get('cs_range', 1e-4))
    path = f"../otids_dataset/{dataset}.csv"

    def generate():
        start = time.time()

        detector = Detector(count=flood_threshold, whitelist=valid_ids, mean_gaps=mean_intervals, slopes=baseline_slopes, error_range=cs_range)

        with open("../otids_dataset/Impersonation_spoof.csv") as f:
            first_row = next(csv.DictReader(f))
            impersonation_start = float(first_row["TS"])

        true_positives = false_positives = true_negatives = false_negatives = 0
        messages_processed = 0
        pending_alerts = []
        flood_ids = set()
        spoof_ids = set()
        clockskew_ids = set()

        if dataset != 'attack_free':
            yield f"data: {json.dumps({'status': 'warming_up', 'messages_processed': 0})}\n\n"
            for i, (msg, _) in enumerate(loader("../otids_dataset/attack_free.csv")):
                detector.process(msg)
                if warmup > 0 and i >= warmup:
                    break
            for rule in detector.rules:
                if rule.name != "ClockskewRule":
                    rule.reset()

        messages = loader(filepath=path)

        for msg, target in messages:
            if path == "../otids_dataset/Impersonation_spoof.csv" and msg.timestamp < impersonation_start + 250:
                continue

            messages_processed += 1
            alerts = detector.process(msg)

            if len(alerts) > 0:
                for alert in alerts:
                    pending_alerts.append(alert)
                    if alert.startswith("Flood"):
                        flood_ids.add(msg.id)
                    elif alert.startswith("Spoof"):
                        spoof_ids.add(msg.id)
                    elif alert.startswith("Clockskew"):
                        clockskew_ids.add(msg.id)
                if target == 0:
                    false_positives += 1
                elif target > 0:
                    true_positives += 1
            else:
                if target == 0:
                    true_negatives += 1
                elif target > 0:
                    false_negatives += 1

            if messages_processed % 2000 == 0:
                yield f"data: {json.dumps({'messages_processed': messages_processed, 'true_positives': true_positives, 'false_positives': false_positives, 'true_negatives': true_negatives, 'false_negatives': false_negatives, 'alerts': pending_alerts[-10:], 'flood_count': len(flood_ids), 'spoof_count': len(spoof_ids), 'clockskew_count': len(clockskew_ids)})}\n\n"
                pending_alerts = []

        elapsed = time.time() - start
        detection_rate = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        false_positive_rate = false_positives / (false_positives + true_negatives) if (false_positives + true_negatives) > 0 else 0
        yield f"data: {json.dumps({'messages_processed': messages_processed, 'true_positives': true_positives, 'false_positives': false_positives, 'true_negatives': true_negatives, 'false_negatives': false_negatives, 'detection_rate': round(detection_rate * 100, 2), 'false_positive_rate': round(false_positive_rate * 100, 2), 'elapsed': round(elapsed, 2), 'flood_count': len(flood_ids), 'spoof_count': len(spoof_ids), 'clockskew_count': len(clockskew_ids), 'done': True})}\n\n"

    return Response(generate(), mimetype='text/event-stream')
    
if __name__ == '__main__':
    app.run(debug=True, threaded=True, use_reloader=False)

