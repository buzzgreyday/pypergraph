sudo dnf install python3-devel gcc gcc-c++ make cmake libffi-devel
source .venv/bin/activate
pip install --upgrade pip
pip install --upgrade cmake scikit-build
python3 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())"
pip install --upgrade pip
pip install coincurve

npm install


npx esbuild sign.ts --bundle --outfile=sign.bundle.js --platform=node --target=node12 