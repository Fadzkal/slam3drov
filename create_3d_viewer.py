import json

def generate_viewer(json_file, html_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
        
    points = data['points']
    colors = data['colors']
    trajectory = data['trajectory']
    target_y = data.get('target_y', 2.0)
    num_points = data['num_points']
    num_waypoints = len(trajectory)
    
    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistem 3D Mapping & Trajectory Tracking - BlueROV2</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0; padding: 0; overflow: hidden;
            background: #050811;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #e2e8f0;
            user-select: none;
        }}
        #header {{
            position: absolute; top: 16px; left: 20px; z-index: 10;
            background: rgba(10, 16, 30, 0.90); backdrop-filter: blur(14px);
            padding: 18px 24px; border-radius: 14px;
            border: 1px solid rgba(0, 229, 255, 0.4);
            box-shadow: 0 16px 40px rgba(0,0,0,0.65);
            max-width: 420px;
        }}
        h1 {{ margin: 0 0 6px 0; font-size: 19px; color: #00e5ff; letter-spacing: 0.5px; font-weight: 700; }}
        p {{ margin: 0 0 10px 0; font-size: 13px; color: #94a3b8; line-height: 1.4; }}
        .badge-row {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }}
        .badge {{
            display: inline-flex; align-items: center; gap: 4px;
            background: rgba(0, 229, 255, 0.15); color: #00e5ff;
            padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600;
            border: 1px solid rgba(0, 229, 255, 0.35);
        }}
        .badge-green {{
            background: rgba(16, 185, 129, 0.15); color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.35);
        }}
        .badge-purple {{
            background: rgba(168, 85, 247, 0.15); color: #c084fc;
            border: 1px solid rgba(168, 85, 247, 0.35);
        }}
        .controls-panel {{
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding-top: 12px; margin-top: 8px;
        }}
        .slider-row {{
            display: flex; align-items: center; justify-content: space-between;
            font-size: 12px; color: #cbd5e1; margin-bottom: 10px;
        }}
        .slider-row input[type=range] {{
            width: 150px; accent-color: #00e5ff; cursor: pointer;
        }}
        .btn-row {{ display: flex; gap: 8px; margin-bottom: 8px; }}
        .btn {{
            flex: 1; padding: 8px 10px; border-radius: 8px;
            font-size: 12px; font-weight: 600; cursor: pointer;
            background: rgba(255, 255, 255, 0.08); color: #e2e8f0;
            border: 1px solid rgba(255, 255, 255, 0.15);
            transition: all 0.2s ease;
            text-align: center;
        }}
        .btn:hover {{
            background: rgba(0, 229, 255, 0.25);
            border-color: #00e5ff; color: #00e5ff;
        }}
        .btn.active {{
            background: rgba(0, 229, 255, 0.9); color: #050811; border-color: #00e5ff;
        }}
        .btn-sim {{
            background: linear-gradient(135deg, #0284c7, #00e5ff);
            color: #050811; font-weight: 700; border: none;
            box-shadow: 0 4px 15px rgba(0, 229, 255, 0.3);
        }}
        .btn-sim:hover {{
            background: linear-gradient(135deg, #0369a1, #38bdf8);
            color: #fff;
        }}
        #legend {{
            position: absolute; top: 16px; right: 20px; z-index: 10;
            background: rgba(10, 16, 30, 0.85); backdrop-filter: blur(10px);
            padding: 14px 18px; border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 12px;
        }}
        .legend-item {{ display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }}
        .legend-item:last-child {{ margin-bottom: 0; }}
        .dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
        .line-dot {{ width: 14px; height: 3px; border-radius: 2px; display: inline-block; }}
        #instructions {{
            position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 10;
            background: rgba(10, 16, 30, 0.90); backdrop-filter: blur(10px);
            padding: 10px 24px; border-radius: 30px;
            font-size: 13px; color: #cbd5e1;
            border: 1px solid rgba(0, 229, 255, 0.3);
            box-shadow: 0 8px 30px rgba(0,0,0,0.5);
            display: flex; gap: 16px; align-items: center;
        }}
        #instructions span {{ display: flex; align-items: center; gap: 6px; }}
        #instructions b {{ color: #00e5ff; font-weight: 600; }}
    </style>
    <script src="static_3d/three.min.js"></script>
    <script src="static_3d/OrbitControls.js"></script>
    <script>
        if (typeof THREE === 'undefined') {{
            document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"><\\/script>');
            document.write('<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"><\\/script>');
        }}
    </script>
</head>
<body>
    <div id="header">
        <h1>3D Mapping & ROV Trajectory</h1>
        <p>Rekonstruksi Inspeksi Kontainer Bawah Laut (Site 113-A)<br>Multi-View Triangulation + 6-DoF Robot Track</p>
        
        <div class="badge-row">
            <span class="badge">📦 {num_points:,} Titik 3D</span>
            <span class="badge badge-green">🛣️ {num_waypoints} Waypoint Lintasan</span>
            <span class="badge badge-purple">🤖 BlueROV2 Active</span>
        </div>

        <div class="controls-panel">
            <div class="btn-row">
                <button class="btn btn-sim" id="btnSim">▶️ Mulai Misi ROV</button>
                <button class="btn" id="btnReset">🎯 Reset View</button>
            </div>
            <div class="btn-row">
                <button class="btn active" id="btnToggleTrack">🛣️ Track ROV: ON</button>
                <button class="btn active" id="btnToggleMesh">📦 Objek 3D: ON</button>
            </div>
            <div class="slider-row">
                <span>Ukuran Titik: <b id="sizeVal">0.18</b></span>
                <input type="range" id="sizeSlider" min="0.04" max="0.5" step="0.02" value="0.18">
            </div>
        </div>
    </div>

    <div id="legend">
        <div class="legend-item"><span class="line-dot" style="background: #00e5ff; box-shadow: 0 0 8px #00e5ff;"></span> <b>Track Jalur Robot</b></div>
        <div class="legend-item"><span class="dot" style="background: #10b981;"></span> Titik Awal (Start)</div>
        <div class="legend-item"><span class="dot" style="background: #ef4444;"></span> Titik Akhir (Goal)</div>
        <div class="legend-item"><span class="dot" style="background: #f59e0b;"></span> Kontainer Bawah Laut</div>
    </div>

    <div id="instructions">
        <span>🖱️ <b>Klik Kiri:</b> Putar 3D</span>
        <span>🔍 <b>Scroll:</b> Zoom In/Out</span>
        <span>✋ <b>Klik Kanan:</b> Geser Posisi</span>
    </div>

    <script>
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x050811);
        scene.fog = new THREE.FogExp2(0x050811, 0.015);

        const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, powerPreference: "high-performance" }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        document.body.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.08;

        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0x00e5ff, 1.2);
        dirLight.position.set(5, 12, 10);
        scene.add(dirLight);

        // Ground Grid
        const gridHelper = new THREE.GridHelper(26, 26, 0x00e5ff, 0x1e293b);
        gridHelper.position.y = 0;
        scene.add(gridHelper);

        // Particle Texture
        function createCircleTexture() {{
            const canvas = document.createElement('canvas');
            canvas.width = 64; canvas.height = 64;
            const ctx = canvas.getContext('2d');
            const grad = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
            grad.addColorStop(0, 'rgba(255,255,255,1.0)');
            grad.addColorStop(0.7, 'rgba(255,255,255,0.85)');
            grad.addColorStop(1, 'rgba(255,255,255,0.0)');
            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.arc(32, 32, 30, 0, Math.PI * 2);
            ctx.fill();
            return new THREE.CanvasTexture(canvas);
        }}

        // 1. Point Cloud (Container)
        const rawPoints = {json.dumps(points)};
        const rawColors = {json.dumps(colors)};

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(rawPoints, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(rawColors, 3));

        const pointMaterial = new THREE.PointsMaterial({{
            size: 0.18,
            vertexColors: true,
            sizeAttenuation: true,
            map: createCircleTexture(),
            transparent: true,
            alphaTest: 0.05
        }});

        const pointCloud = new THREE.Points(geometry, pointMaterial);
        scene.add(pointCloud);

        // 2. Trajectory Track
        const rawTraj = {json.dumps(trajectory)};
        const trajVectors = rawTraj.map(p => new THREE.Vector3(p[0], p[1], p[2]));
        const curve = new THREE.CatmullRomCurve3(trajVectors);

        const trackGroup = new THREE.Group();

        // Glowing tube along the path
        const tubeGeometry = new THREE.TubeGeometry(curve, 120, 0.06, 8, false);
        const tubeMaterial = new THREE.MeshBasicMaterial({{
            color: 0x00e5ff,
            transparent: true,
            opacity: 0.85
        }});
        const trajectoryTube = new THREE.Mesh(tubeGeometry, tubeMaterial);
        trackGroup.add(trajectoryTube);

        // Waypoint markers
        rawTraj.forEach((p, idx) => {{
            let color = 0x00e5ff;
            let radius = 0.07;
            if (idx === 0) {{
                color = 0x10b981; // Green start
                radius = 0.14;
            }} else if (idx === rawTraj.length - 1) {{
                color = 0xef4444; // Red end
                radius = 0.14;
            }}
            const sphereGeo = new THREE.SphereGeometry(radius, 12, 12);
            const sphereMat = new THREE.MeshBasicMaterial({{ color: color }});
            const sphere = new THREE.Mesh(sphereGeo, sphereMat);
            sphere.position.set(p[0], p[1], p[2]);
            trackGroup.add(sphere);
        }});

        scene.add(trackGroup);

        // 3. Mini BlueROV2 Model
        const rovGroup = new THREE.Group();
        
        // Chassis Body
        const bodyGeo = new THREE.BoxGeometry(0.5, 0.28, 0.65);
        const bodyMat = new THREE.MeshStandardMaterial({{ color: 0x0284c7, metalness: 0.7, roughness: 0.3 }});
        const body = new THREE.Mesh(bodyGeo, bodyMat);
        rovGroup.add(body);

        // Thruster Tubes
        const tubeMat = new THREE.MeshStandardMaterial({{ color: 0x0f172a, metalness: 0.8 }});
        [-0.28, 0.28].forEach(xOff => {{
            const thrusterGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.5, 12);
            thrusterGeo.rotateX(Math.PI / 2);
            const thruster = new THREE.Mesh(thrusterGeo, tubeMat);
            thruster.position.set(xOff, 0, 0);
            rovGroup.add(thruster);
        }});

        // Front Camera Dome
        const domeGeo = new THREE.SphereGeometry(0.12, 16, 16);
        const domeMat = new THREE.MeshStandardMaterial({{ color: 0x38bdf8, transparent: true, opacity: 0.85, roughness: 0.1 }});
        const dome = new THREE.Mesh(domeGeo, domeMat);
        dome.position.set(0, 0.04, -0.34);
        rovGroup.add(dome);

        // Searchlight Spotlight
        const spotLight = new THREE.SpotLight(0x00e5ff, 3, 10, Math.PI / 5, 0.5);
        spotLight.position.set(0, 0.04, -0.34);
        const spotTarget = new THREE.Object3D();
        spotTarget.position.set(0, 0, -5);
        rovGroup.add(spotTarget);
        spotLight.target = spotTarget;
        rovGroup.add(spotLight);

        // Initial ROV placement at start
        if (trajVectors.length > 0) {{
            rovGroup.position.copy(trajVectors[0]);
            if (trajVectors.length > 1) {{
                rovGroup.lookAt(trajVectors[1]);
            }}
        }}
        scene.add(rovGroup);

        // Camera framing
        const defaultTarget = new THREE.Vector3(0, {target_y:.2f}, 0);
        const defaultCamPos = new THREE.Vector3(0, {target_y + 4.5:.2f}, 14.0);

        function resetCamera() {{
            controls.target.copy(defaultTarget);
            camera.position.copy(defaultCamPos);
            controls.update();
        }}
        resetCamera();

        // UI Controls
        const sizeSlider = document.getElementById('sizeSlider');
        const sizeVal = document.getElementById('sizeVal');
        sizeSlider.addEventListener('input', (e) => {{
            const val = parseFloat(e.target.value);
            pointMaterial.size = val;
            sizeVal.innerText = val.toFixed(2);
        }});

        const btnToggleTrack = document.getElementById('btnToggleTrack');
        btnToggleTrack.addEventListener('click', () => {{
            trackGroup.visible = !trackGroup.visible;
            btnToggleTrack.innerText = trackGroup.visible ? '🛣️ Track ROV: ON' : '🛣️ Track ROV: OFF';
            btnToggleTrack.classList.toggle('active', trackGroup.visible);
        }});

        const btnToggleMesh = document.getElementById('btnToggleMesh');
        btnToggleMesh.addEventListener('click', () => {{
            pointCloud.visible = !pointCloud.visible;
            btnToggleMesh.innerText = pointCloud.visible ? '📦 Objek 3D: ON' : '📦 Objek 3D: OFF';
            btnToggleMesh.classList.toggle('active', pointCloud.visible);
        }});

        let isSimulating = false;
        let simProgress = 0;
        const btnSim = document.getElementById('btnSim');
        btnSim.addEventListener('click', () => {{
            isSimulating = !isSimulating;
            btnSim.innerText = isSimulating ? '⏸️ Pause Misi' : '▶️ Lanjut Misi';
            btnSim.classList.toggle('active', isSimulating);
        }});

        document.getElementById('btnReset').addEventListener('click', () => {{
            resetCamera();
        }});

        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});

        function animate() {{
            requestAnimationFrame(animate);

            if (isSimulating && curve) {{
                simProgress += 0.0025;
                if (simProgress > 1.0) simProgress = 0;
                const pos = curve.getPointAt(simProgress);
                const tangent = curve.getTangentAt(simProgress);
                rovGroup.position.copy(pos);
                rovGroup.lookAt(pos.clone().add(tangent));
            }}

            controls.update();
            renderer.render(scene, camera);
        }}
        animate();
    </script>
</body>
</html>
"""
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Viewer 3D dengan Track Lintasan Robot tersimpan di: {html_file}")

if __name__ == "__main__":
    generate_viewer(r"c:\remote_ROV\reconstruction_data.json", r"c:\remote_ROV\view_3d_container.html")
