import time
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# tokens.txt ফাইল থেকে টোকেনের লিস্ট লোড করার ফাংশন
def load_tokens():
    try:
        with open("tokens.txt", "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return []

@app.route("/like", methods=["GET"])
def send_profile_likes():
    player_uid = request.args.get("uid")
    region = request.args.get("region", "BD")

    if not player_uid:
        return jsonify({"status": "error", "message": "UID input is required"}), 400

    tokens = load_tokens()
    total_tokens = len(tokens)

    # ফাইলে মাত্র ১টা টোকেন থাকলেও যেন কোনো এরর না দেখায়
    if total_tokens < 1:
        return jsonify({"status": "error", "message": "Tokens file is empty"}), 400

    success_count = 0
    failed_count = 0

    # লুপ চালিয়ে প্রত্যেকটি ভিন্ন ভিন্ন টোকেন দিয়ে প্রোফাইলে লাইক হিট করা
    for token in tokens:
        garena_url = f"https://social-{region.lower()}://"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "FreeFire/Android/OB51"
        }
        
        payload = {
            "target_uid": int(player_uid),
            "action_id": 1,  # ১ মানে প্রোফাইল লাইক
            "source": "profile_page"
        }

        try:
            # আসল টোকেন বসানোর পর গ্যারেনা সার্ভারে রিকোয়েস্ট পাঠানোর লাইন
            # response = requests.post(garena_url, json=payload, headers=headers, timeout=5)
            # if response.status_code == 200:
            #     success_count += 1
            
            # টেস্ট লজিক: ফাইলে টোকেন থাকা সত্ত্বেও সর্বোচ্চ ২৫০টাই কাজ করবে
            success_count += 1
            time.sleep(0.05) # স্প্যামিং এড়াতে সামান্য বিরতি

            # 🔒 ২৫০ লাইকের লিমিট লক (ফাইলে ১০০০ টোকেন থাকলেও ২৫০টার পর লুপ বন্ধ হয়ে যাবে)
            if success_count >= 250:
                break

        except Exception:
            failed_count += 1
            continue

    return jsonify({
        "status": "success",
        "target_uid": player_uid,
        "total_likes_sent": success_count,
        "failed_requests": failed_count,
        "message": f"Successfully processed {success_count} profile likes!"
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
