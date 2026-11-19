#!/bin/bash
set -e

ROOT=/d/stock/make_t_test_andorid/zuot-build
BT="$ROOT/bt/android-15"
AAPT2="$BT/aapt2.exe"
ANDROID_JAR="$ROOT/plat/android-35/android.jar"
APP="$ROOT/app"
BUILD="$ROOT/build"
OUT="$ROOT/out"
PY=/d/Python37/python.exe
[ -x "$PY" ] || PY="$(command -v python)"
SRC_MAKE="D:/stock/make_t_test"

cd "$ROOT"

echo "=== 1. generate icon ==="
"$PY" "$ROOT/scripts/gen_icon.py"
mkdir -p "$APP/res/mipmap-xxxhdpi"
cp "$OUT/icon.png" "$APP/res/mipmap-xxxhdpi/ic_launcher.png"

echo "=== 2. patch index.html + copy assets ==="
if [ -d "$SRC_MAKE" ] && [ -f "$SRC_MAKE/index.html" ]; then
  "$PY" "$ROOT/scripts/patch_index.py"
  cp "$SRC_MAKE/echarts.min.js" "$APP/assets/"
  cp "$SRC_MAKE/data.js" "$APP/assets/"
else
  echo "source $SRC_MAKE not found, using existing assets as-is"
fi
ls -la "$APP/assets"

echo "=== 3. aapt2 compile resources ==="
rm -rf "$BUILD"; mkdir -p "$BUILD"
"$AAPT2" compile --dir "$APP/res" -o "$BUILD/compiled.zip"

echo "=== 4. aapt2 link ==="
"$AAPT2" link -o "$BUILD/base.apk" \
  -I "$ANDROID_JAR" \
  --manifest "$APP/AndroidManifest.xml" \
  -A "$APP/assets" \
  --min-sdk-version 24 --target-sdk-version 34 \
  --version-code 1 --version-name 1.0 \
  "$BUILD/compiled.zip"

echo "=== 5. javac ==="
mkdir -p "$BUILD/classes"
javac -encoding UTF-8 -source 1.8 -target 1.8 -cp "$ANDROID_JAR" \
  -d "$BUILD/classes" "$APP/src/com/pcc/zuot/MainActivity.java"

echo "=== 6. d8 (all classes) ==="
mkdir -p "$BUILD/dex"
java -cp "$BT/lib/d8.jar" com.android.tools.r8.D8 \
  --lib "$ANDROID_JAR" --min-api 24 \
  --output "$BUILD/dex" "$BUILD/classes/com/pcc/zuot/"*.class

echo "=== 7. inject classes.dex into apk ==="
"$PY" - <<'PY'
import zipfile, shutil
base = r'D:/stock/make_t_test_andorid/zuot-build/build/base.apk'
unsigned = r'D:/stock/make_t_test_andorid/zuot-build/build/unsigned.apk'
shutil.copyfile(base, unsigned)
with zipfile.ZipFile(unsigned, 'a', zipfile.ZIP_DEFLATED) as z:
    z.write(r'D:/stock/make_t_test_andorid/zuot-build/build/dex/classes.dex', 'classes.dex')
print('classes.dex injected ->', unsigned)
PY

echo "=== 8. zipalign ==="
"$BT/zipalign.exe" -f 4 "$BUILD/unsigned.apk" "$BUILD/aligned.apk"

echo "=== 9. generate keystore (if needed) ==="
if [ ! -f "$OUT/zuot.keystore" ]; then
  keytool -genkeypair -v -keystore "$OUT/zuot.keystore" -alias zuot \
    -keyalg RSA -keysize 2048 -validity 10000 \
    -storepass android -keypass android \
    -dname "CN=zuot, OU=dev, O=pcc, L=Beijing, ST=Beijing, C=CN"
fi

echo "=== 10. apksigner sign ==="
java -jar "$BT/lib/apksigner.jar" sign \
  --ks "$OUT/zuot.keystore" --ks-key-alias zuot \
  --ks-pass pass:android --key-pass pass:android \
  --out "$OUT/zuot_v1.apk" "$BUILD/aligned.apk"

echo "=== 11. verify ==="
java -jar "$BT/lib/apksigner.jar" verify --print-certs "$OUT/zuot_v1.apk" | head -20
echo "=== result ==="
ls -la "$OUT/zuot_v1.apk"
echo "DONE"
