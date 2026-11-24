# Vigenère Cipher Decrypter
# Python cryptanalysis implementation


import base64
import io
import collections
import itertools
import math
import string

import matplotlib.pyplot as plt

english_freqs = {
    'A': 8.167, 'B': 1.492, 'C': 2.782, 'D': 4.253, 'E': 12.702, 'F': 2.228,
    'G': 2.015, 'H': 6.094, 'I': 6.966, 'J': 0.153, 'K': 0.772, 'L': 4.025,
    'M': 2.406, 'N': 6.749, 'O': 7.507, 'P': 1.929, 'Q': 0.095, 'R': 5.987,
    'S': 6.327, 'T': 9.056, 'U': 2.758, 'V': 0.978, 'W': 2.360, 'X': 0.150,
    'Y': 1.974, 'Z': 0.074
}

alphabet = list(string.ascii_uppercase)

def analyze_ciphertext(ciphertext):
  cleaned_text = "".join([char.upper() for char in ciphertext if char.isalpha()])
  
  # Sort alphabet characters by standard English frequency (highest to lowest)
  sorted_english_chars = sorted(english_freqs.keys(), key=lambda x: english_freqs[x], reverse=True)
  sorted_english_vals = [english_freqs[c] for c in sorted_english_chars]
  
  # --- 1. FREQUENCY ANALYSIS & DETERMINING SUITABLE BINS (UP TO 40) ---
  matching_key_length = None
  found_bins = None
  
  print("Key length search (from 1 to 40 Bins):")
  html_output = "<pre style='line-height:1.2;'>"
  
  for k in range(1, 41):
      test_bins = {i: [] for i in range(k)}
      for index, char in enumerate(cleaned_text):
          test_bins[index % k].append(char)
  
      matching_bins_count = 0
      for bin_idx in range(k):
          bin_chars = test_bins[bin_idx]
          if not bin_chars:
              continue
  
          counts = collections.Counter(bin_chars)
          total_chars = len(bin_chars)
          pcts = [(counts.get(char, 0) / total_chars) * 100 for char in alphabet]
  
          cond_over_10 = any(p > 10.0 for p in pcts)
          cond_under_1 = sum(1 for p in pcts if p < 1.0) >= 4
  
          if cond_over_10 and cond_under_1:
              matching_bins_count += 1
  
      ratio = matching_bins_count / k
      bold_condition = ratio > 0.5
  
      line = f"Bins: {k:<2} | Matching condition: {matching_bins_count} out of {k} ({ratio*100:.1f}%)"
      if bold_condition:
          html_output += f"<b>{line}</b>\n"
      else:
          html_output += f"{line}\n"
  
      # Pick first matching key length (minimum 3 bins or all bins if small k)
      threshold = min(3, k)
      if matching_key_length is None and matching_bins_count >= threshold:
          matching_key_length = k
          found_bins = test_bins
  
  html_output += "</pre>"
  if matching_key_length is None:
    return {"error": "Could not identify a suitable key length."}
  
  # --- 2. MAKE RELATIVE FREQUENCY PLOTS FOR SELECTED CONFIGURATION ---
  if matching_key_length is not None:
      print(f"\nFirst suitable bin configuration chosen: {matching_key_length} Bins\n")
  
      fig, axes = plt.subplots(matching_key_length, 1, figsize=(12, 5.0 * matching_key_length))
      if matching_key_length == 1:
          axes = [axes]
      else:
          axes = axes.flatten()
  
      # Setup decryption helpers
      def decrypt_caesar(text, shift):
          return ''.join(alphabet[(alphabet.index(c) - shift) % 26] for c in text)
  
      def chi_squared(text):
          n = len(text)
          score = 0
          for i, letter in enumerate(alphabet):
              observed = text.count(letter)
              expected = n * english_freqs[letter] / 100
              score += (observed - expected) ** 2 / expected
          return score
  
      bin_candidates = []
  
      for bin_idx in range(matching_key_length):
          bin_chars = found_bins[bin_idx]
          counts = collections.Counter(bin_chars)
          total_chars = len(bin_chars) if len(bin_chars) > 0 else 1
  
          # Process actual ciphertext bin frequencies sorted descending
          pct_data = {char: (counts.get(char, 0) / total_chars) * 100 for char in alphabet}
          sorted_actual_chars = sorted(alphabet, key=lambda x: pct_data[x], reverse=True)
          sorted_actual_vals = [pct_data[c] for c in sorted_actual_chars]
  
          # Plot overlay of both sorted descending (they do not align by letter, only shape match)
          ax = axes[bin_idx]
          x_indices = range(26)
          ax.bar(x_indices, sorted_actual_vals, color='royalblue', alpha=0.85, edgecolor='black', label='Actual (Sorted)')
          ax.bar(x_indices, sorted_english_vals, color='crimson', alpha=0.35, edgecolor='crimson', label='English Ref (Sorted)')
  
          ax.set_title(f'Bin {bin_idx} Frequencies vs English Reference (Both Sorted Descending | Total: {len(bin_chars)} chars)', fontsize=11, fontweight='bold')
          ax.set_ylabel('Relative Frequency (%)')
          ax.set_xlim(-0.5, 25.5)
  
          # Create dual color-coded x-axis labels
          ax.set_xticks(x_indices)
          dual_labels = [f"{act}\n{eng}" for act, eng in zip(sorted_actual_chars, sorted_english_chars)]
          ax.set_xticklabels(dual_labels, fontsize=10)
  
          # Color code the individual tick labels
          for tick, act_char, eng_char in zip(ax.get_xticklabels(), sorted_actual_chars, sorted_english_chars):
              # We can use colored text formatting hacks or dual text drawing. Since matplotlib can't easily
              # multi-color one text string natively, we can draw a custom legend / description
              pass
  
          ax.text(-0.02, -0.08, 'Cipher (Blue):\nEnglish (Red):', transform=ax.transAxes,
                  fontsize=9, color='black', ha='right', va='center', fontweight='bold')
  
          ax.legend()
          ax.grid(True, axis='y', linestyle='--', alpha=0.5)
  
          # Solve shift ranking using chi-squared for key guess assembly
          results = []
          for shift in range(26):
              decrypted = decrypt_caesar(bin_chars, shift)
              score = chi_squared(decrypted)
              results.append((score, shift))
          results.sort()
  
          bin_candidates.append(results[:5]) # Store top 5 shifts for this bin
  
      plt.suptitle(f'Vigenère Bin Frequency Plots: Shape Comparison (Key Length = {matching_key_length})\n(Note: X-Axis contains top Cipher character in Blue and top English character in Red)', fontsize=13, fontweight='bold', y=1.002)
      plt.tight_layout()
      #plt.show()
      image_buffer = io.BytesIO()
      plt.savefig(image_buffer, format="png", bbox_inches="tight")
      image_buffer.seek(0)
      plot_base64 = base64.b64encode(image_buffer.read()).decode("utf-8")
      plt.close(fig)
  
      # --- 3. PRINT TOP CANDIDATES AND KEY GUESS ASSEMBLY ---
      print("\n" + "="*40)
      print("TOP 5 CANDIDATES PER KEY LETTER POSITION")
      print("="*40)
      for idx, cand_list in enumerate(bin_candidates):
          print(f"\n--- Bin {idx} ---")
          for rank, (score, shift) in enumerate(cand_list):
              print(f"Candidate #{rank+1}: {alphabet[shift]} | Shift: {shift:2} | Chi-squared Score: {score:.2f}")
  
      print("\n" + "="*40)
      print("TOP 5 CANDIDATE KEY GUESSES")
      print("="*40)
      for r in range(5):
          key_guess = ""
          for bin_idx in range(matching_key_length):
              key_guess += alphabet[bin_candidates[bin_idx][r][1]]
          print(f"Guess #{r+1}: {key_guess}")
  
  # --- 1. LOAD TETRAGRAM DATA DIRECTLY FROM LOCAL FILE ---
  
  
  local_filename = "/english_quadgrams.txt"
  quadgrams = {}
  
  try:
      with open(local_filename, "r") as file:
          for line in file:
              if line.strip():
                  parts = line.strip().split()
                  if len(parts) == 2:
                      key, count = parts[0].upper(), int(parts[1])
                      quadgrams[key] = count
      print(f"Successfully loaded {len(quadgrams)} tetragrams from local file.")
  except Exception as e:
      print(f"Error reading local file: {e}. Using fallback...")
      quadgrams = {}
  
  # Calculate total count & log probabilities
  total_quadgrams = sum(quadgrams.values()) if quadgrams else 1
  log_quadgrams = {}
  for k, val in quadgrams.items():
      log_quadgrams[k] = math.log10(val / total_quadgrams)
  
  # Floor value for unseen quadgrams
  floor_val = math.log10(0.01 / total_quadgrams)
  
  def score_text(text):
      score = 0
      clean = "".join([c.upper() for c in text if c.isalpha()])
      for i in range(len(clean) - 3):
          quad = clean[i:i+4]
          if quad in log_quadgrams:
              score += log_quadgrams[quad]
          else:
              score += floor_val
      return score
  
  
  # --- 2. DECRYPTION HELPER FUNCTION ---
  def vigenere_decrypt(ciphertext, key):
      decrypted_chars = []
      key_len = len(key)
      key_shifts = [alphabet.index(k_char) for k_char in key]
  
      for i, char in enumerate(ciphertext):
          if char in alphabet:
              shift = key_shifts[i % key_len]
              decrypted_char = alphabet[(alphabet.index(char) - shift) % 26]
              decrypted_chars.append(decrypted_char)
          else:
              decrypted_chars.append(char)
      return "".join(decrypted_chars)
  
  
  # --- 3. DYNAMICALLY GENERATE COMBINATIONS AND SCORE THEM ---
  key_len = matching_key_length
  
  # Get top 2 candidates for each bin from dynamic variable
  dynamic_top_2 = []
  for bin_idx in range(key_len):
      candidates = [alphabet[shift] for (score, shift) in bin_candidates[bin_idx][:2]]
      dynamic_top_2.append(candidates)
  
  print(f"Key Length: {key_len}")
  for idx, cand in enumerate(dynamic_top_2):
      print(f"  Bin {idx} candidates: {cand}")
  
  all_keys_scored = []
  
  # Generate Cartesian product (2 ^ key_len keys)
  for key_tuple in itertools.product(*dynamic_top_2):
      key = "".join(key_tuple)
      decrypted = vigenere_decrypt(cleaned_text, key)
      score = score_text(decrypted)
      all_keys_scored.append((score, key, decrypted))
  
  # Sort by score descending
  all_keys_scored.sort(key=lambda x: x[0], reverse=True)
  
  
  # --- 4. PRINT DECRYPTION RESULTS ---
  print(f"Analyzed {len(all_keys_scored)} key candidates.\n")
  
  print("="*60)
  print("TOP 10 KEYS SORTED BY TETRAGRAM SCORE")
  print("="*60)
  for rank, (score, key, _) in enumerate(all_keys_scored[:10], 1):
      print(f"Rank #{rank:2}: Key = {key} | Score = {score:.2f}")
  
    top_results = []

  for rank, (score, key, decrypted) in enumerate(all_keys_scored[:5], 1):
      top_results.append({
          "rank": rank,
          "key": key,
          "score": round(score, 2),
          "decrypted_text": decrypted[:400]
      })

  return {
      "key_length": key_len,
      "analyzed_candidates": len(all_keys_scored),
      "plot": plot_base64,
      "results": top_results
  }








