import json
import os

def generate_metric_viewer(json_path, output_html_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    meta = data['metadata']
    dims = meta['dimensions_meters']
    num_points = meta['num_points']
    num_waypoints = meta['num_waypoints']
    
    # Read points, colors, trajectory, telemetry
    points_json = json.dumps(data['points'])
    colors_json = json.dumps(data['colors'])
    trajectory_json = json.dumps(data['trajectory'])
    telemetry_json = json.dumps(data['telemetry'])
    dims_json = json.dumps(dims)
    
    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subsea Metric 3D Mapping & Multi-Sensor Fusion - BlueROV2</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            overflow: hidden;
            background: #030712;
            font-family: 'Inter', -apple-system, sans-serif;
            color: #f1f5f9;
            user-select: none;
        }}
        
        /* Top Navigation Header */
        #top-bar {{
            position: absolute; top: 16px; left: 20px; z-index: 20;
            background: rgba(10, 17, 34, 0.88); backdrop-filter: blur(16px);
            padding: 16px 22px; border-radius: 16px;
            border: 1px solid rgba(0, 229, 255, 0.35);
            box-shadow: 0 20px 45px rgba(0, 0, 0, 0.7);
            max-width: 440px;
        }}
        .header-title {{
            display: flex; align-items: center; gap: 10px;
            margin-bottom: 6px;
        }}
        .status-dot {{
            width: 10px; height: 10px; border-radius: 50%;
            background: #10b981; box-shadow: 0 0 10px #10b981;
            animation: pulse-dot 2s infinite;
        }}
        @keyframes pulse-dot {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.4; transform: scale(0.85); }}
        }}
        h1 {{
            font-size: 17px; font-weight: 800; color: #00e5ff;
            letter-spacing: 0.4px; text-transform: uppercase;
        }}
        .subtitle {{
            font-size: 12px; color: #94a3b8; line-height: 1.45; margin-bottom: 12px;
        }}
        .badges-row {{
            display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px;
        }}
        .badge {{
            display: inline-flex; align-items: center; gap: 5px;
            background: rgba(0, 229, 255, 0.12); color: #00e5ff;
            padding: 4px 9px; border-radius: 6px; font-size: 11px; font-weight: 600;
            border: 1px solid rgba(0, 229, 255, 0.3); font-family: 'JetBrains Mono', monospace;
        }}
        .badge-green {{
            background: rgba(16, 185, 129, 0.12); color: #10b981;
            border-color: rgba(16, 185, 129, 0.3);
        }}
        .badge-purple {{
            background: rgba(168, 85, 247, 0.12); color: #c084fc;
            border-color: rgba(168, 85, 247, 0.3);
        }}

        /* Sensor Telemetry HUD (Right Panel) */
        #telemetry-hud {{
            position: absolute; top: 16px; right: 20px; z-index: 20;
            background: rgba(10, 17, 34, 0.88); backdrop-filter: blur(16px);
            padding: 16px 20px; border-radius: 16px;
            border: 1px solid rgba(0, 229, 255, 0.35);
            box-shadow: 0 20px 45px rgba(0, 0, 0, 0.7);
            width: 320px;
        }}
        .panel-heading {{
            font-size: 12px; font-weight: 700; color: #64748b;
            text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;
            display: flex; justify-content: space-between; align-items: center;
        }}
        .telemetry-card {{
            background: rgba(15, 23, 42, 0.65);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px; padding: 10px 12px; margin-bottom: 10px;
        }}
        .telemetry-card.highlight {{
            border-color: rgba(0, 229, 255, 0.4);
            background: rgba(0, 229, 255, 0.05);
        }}
        .sensor-label {{
            font-size: 11px; color: #94a3b8; font-weight: 600;
            display: flex; align-items: center; justify-content: space-between;
            margin-bottom: 4px;
        }}
        .sensor-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 20px; font-weight: 700; color: #00e5ff;
            letter-spacing: -0.5px;
        }}
        .sensor-unit {{ font-size: 12px; font-weight: 500; color: #64748b; margin-left: 2px; }}
        .sensor-sub {{
            font-size: 11px; color: #64748b; margin-top: 3px; font-family: 'JetBrains Mono', monospace;
        }}

        /* Dimension Box HUD */
        .dim-grid {{
            display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px;
            margin-top: 6px; text-align: center;
        }}
        .dim-cell {{
            background: rgba(30, 41, 59, 0.5); padding: 6px 4px; border-radius: 6px;
        }}
        .dim-cell span {{ font-size: 10px; color: #94a3b8; display: block; }}
        .dim-cell b {{ font-size: 12px; color: #38bdf8; font-family: 'JetBrains Mono', monospace; }}

        /* Bottom Controls Bar */
        #bottom-panel {{
            position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 20;
            background: rgba(10, 17, 34, 0.92); backdrop-filter: blur(16px);
            padding: 12px 24px; border-radius: 20px;
            border: 1px solid rgba(0, 229, 255, 0.35);
            box-shadow: 0 16px 40px rgba(0,0,0,0.7);
            display: flex; align-items: center; gap: 20px;
            max-width: 90vw;
        }}
        .playback-controls {{
            display: flex; align-items: center; gap: 8px;
        }}
        .btn {{
            padding: 8px 14px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.15);
            background: rgba(255, 255, 255, 0.06); color: #e2e8f0;
            font-size: 12px; font-weight: 600; cursor: pointer;
            transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 6px;
        }}
        .btn:hover {{
            background: rgba(0, 229, 255, 0.2); border-color: #00e5ff; color: #00e5ff;
        }}
        .btn.active {{
            background: #00e5ff; color: #030712; border-color: #00e5ff; font-weight: 700;
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #0284c7, #00e5ff);
            color: #030712; font-weight: 700; border: none;
            box-shadow: 0 4px 15px rgba(0, 229, 255, 0.35);
        }}
        .btn-primary:hover {{
            background: linear-gradient(135deg, #0369a1, #38bdf8); color: #fff;
        }}
        
        /* Timeline Slider */
        .timeline-container {{
            display: flex; align-items: center; gap: 12px; min-width: 280px;
        }}
        .timeline-slider {{
            flex: 1; accent-color: #00e5ff; cursor: pointer; height: 6px;
        }}
        .timeline-label {{
            font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #cbd5e1;
            min-width: 50px; text-align: right;
        }}

        /* View Mode Buttons */
        .view-modes {{
            display: flex; gap: 6px; border-left: 1px solid rgba(255, 255, 255, 0.15);
            padding-left: 16px;
        }}

        /* Viewport Canvas Overlay */
        #crosshair {{
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            width: 40px; height: 40px; pointer-events: none; z-index: 5;
            display: none;
        }}
        #crosshair::before, #crosshair::after {{
            content: ''; position: absolute; background: rgba(0, 229, 255, 0.6);
        }}
        #crosshair::before {{ top: 19px; left: 0; width: 40px; height: 2px; }}
        #crosshair::after {{ top: 0; left: 19px; width: 2px; height: 40px; }}

        /* Instructions Tip */
        #instructions-tip {{
            position: absolute; bottom: 84px; left: 50%; transform: translateX(-50%); z-index: 10;
            background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(8px);
            padding: 6px 16px; border-radius: 20px; font-size: 11px; color: #94a3b8;
            border: 1px solid rgba(255, 255, 255, 0.08); pointer-events: none;
        }}
    </style>
    <!-- Three.js with fallback -->
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
    <div id="crosshair"></div>

    <!-- Header Panel -->
    <div id="top-bar">
        <div class="header-title">
            <span class="status-dot"></span>
            <h1>Metric 3D Subsea Survey</h1>
        </div>
        <p class="subtitle">
            Rekonstruksi Objek Bawah Laut (Site 113-A Steel Container)<br>
            Fusi Skala Kamera HD + Ping1D Sonar + Bar30 Depth Sensor
        </p>
        
        <div class="badges-row">
            <span class="badge">📦 {num_points:,} Titik Metrik</span>
            <span class="badge badge-green">📡 Ping1D Metric Scale: ACTIVE</span>
            <span class="badge badge-purple">🌊 Bar30 Z: LOCKED</span>
        </div>

        <div style="display: flex; gap: 8px;">
            <button class="btn active" id="btnToggleSonar">🔊 Sinar Sonar: ON</button>
            <button class="btn active" id="btnToggleTrack">🛣️ Jalur Track: ON</button>
            <button class="btn" id="btnToggleBox">📏 Bounding Box</button>
        </div>
    </div>

    <!-- Telemetry HUD -->
    <div id="telemetry-hud">
        <div class="panel-heading">
            <span>Telemetri Sensor ROV</span>
            <span style="color: #00e5ff; font-family: 'JetBrains Mono', monospace;" id="waypointBadge">WP 0/{num_waypoints}</span>
        </div>

        <!-- Ping1D Sonar Card -->
        <div class="telemetry-card highlight">
            <div class="sensor-label">
                <span>🎯 PING1D ACOUSTIC STANDOFF</span>
                <span id="sonarConf" style="color: #10b981;">96% CONF</span>
            </div>
            <div>
                <span class="sensor-value" id="sonarDist">2.75</span>
                <span class="sensor-unit">meter</span>
            </div>
            <div class="sensor-sub" id="sonarStatus">Acoustic Anchor to Surface Target</div>
        </div>

        <!-- Bar30 Depth Card -->
        <div class="telemetry-card">
            <div class="sensor-label">
                <span>🌊 BAR30 HYDROSTATIC DEPTH</span>
                <span id="bar30Pressure" style="color: #38bdf8;">2336 mbar</span>
            </div>
            <div>
                <span class="sensor-value" id="bar30Depth" style="color: #38bdf8;">-13.50</span>
                <span class="sensor-unit">meter</span>
            </div>
            <div class="sensor-sub">Ground-Truth Vertical Z Position</div>
        </div>

        <!-- IMU Attitude Card -->
        <div class="telemetry-card">
            <div class="sensor-label">
                <span>🧭 ARDUSUB IMU ATTITUDE</span>
                <span>6-DoF</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 4px; font-family: 'JetBrains Mono', monospace; font-size: 13px;">
                <span>R: <b id="imuRoll" style="color: #f1f5f9;">0.0°</b></span>
                <span>P: <b id="imuPitch" style="color: #f1f5f9;">0.0°</b></span>
                <span>Y: <b id="imuYaw" style="color: #00e5ff;">0.0°</b></span>
            </div>
        </div>

        <!-- Physical Dimensions Card -->
        <div class="telemetry-card">
            <div class="sensor-label">
                <span>📐 HASIL UKURAN FISIK OBJEK 3D</span>
            </div>
            <div class="dim-grid">
                <div class="dim-cell"><span>Panjang (X)</span><b>{dims['length']} m</b></div>
                <div class="dim-cell"><span>Tinggi (Y)</span><b>{dims['height']} m</b></div>
                <div class="dim-cell"><span>Lebar (Z)</span><b>{dims['width']} m</b></div>
            </div>
        </div>
    </div>

    <!-- Instructions Tip -->
    <div id="instructions-tip">
        🖱️ <b>Klik Kiri:</b> Putar 3D | 🔍 <b>Scroll:</b> Zoom | ✋ <b>Klik Kanan:</b> Geser | 🎯 <b>Ukuran Grid:</b> 1.0 Meter
    </div>

    <!-- Bottom Controls Bar -->
    <div id="bottom-panel">
        <div class="playback-controls">
            <button class="btn btn-primary" id="btnPlayPause">▶️ Putar Misi</button>
            <button class="btn" id="btnReset">⏪ Reset</button>
        </div>

        <div class="timeline-container">
            <input type="range" class="timeline-slider" id="timelineSlider" min="0" max="{num_waypoints - 1}" value="0" step="1">
            <span class="timeline-label" id="timelineText">0/{num_waypoints - 1}</span>
        </div>

        <div class="view-modes">
            <button class="btn active" id="viewOrbit">🌐 Orbit 3D</button>
            <button class="btn" id="viewFPV">🎥 FPV ROV</button>
            <button class="btn" id="viewTopDown">🗺️ Bathymetry</button>
        </div>
    </div>

    <script>
        // Data Payload
        const pointsData = {points_json};
        const colorsData = {colors_json};
        const trajectoryData = {trajectory_json};
        const telemetryData = {telemetry_json};
        const dimsData = {dims_json};

        const numWaypoints = trajectoryData.length;

        // Scene Setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x030712);
        scene.fog = new THREE.FogExp2(0x030712, 0.025);

        const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(6, 6, 9);

        const renderer = new THREE.WebGLRenderer({{ antialias: true, powerPreference: "high-performance" }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        document.body.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.08;
        controls.target.set(0, 1.5, 0);

        // Lighting
        const ambLight = new THREE.AmbientLight(0xffffff, 0.65);
        scene.add(ambLight);

        const dirLight = new THREE.DirectionalLight(0x00e5ff, 1.4);
        dirLight.position.set(10, 20, 15);
        scene.add(dirLight);

        const blueLight = new THREE.PointLight(0x0284c7, 2.0, 30);
        blueLight.position.set(-10, 5, -10);
        scene.add(blueLight);

        // Metric Ground Grid (1 Meter Squares)
        const gridHelper = new THREE.GridHelper(20, 20, 0x00e5ff, 0x1e293b);
        gridHelper.position.y = 0;
        scene.add(gridHelper);

        // Reconstructed 3D Metric Point Cloud
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(pointsData, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colorsData, 3));

        // Soft Circular Particle Texture
        function createPointTexture() {{
            const canvas = document.createElement('canvas');
            canvas.width = 64; canvas.height = 64;
            const ctx = canvas.getContext('2d');
            const grad = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
            grad.addColorStop(0, 'rgba(255,255,255,1.0)');
            grad.addColorStop(0.65, 'rgba(255,255,255,0.85)');
            grad.addColorStop(1, 'rgba(255,255,255,0)');
            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.arc(32, 32, 30, 0, Math.PI * 2);
            ctx.fill();
            return new THREE.CanvasTexture(canvas);
        }}

        const pMaterial = new THREE.PointsMaterial({{
            size: 0.16,
            vertexColors: true,
            map: createPointTexture(),
            transparent: true,
            opacity: 0.95,
            alphaTest: 0.05
        }});

        const pointCloud = new THREE.Points(geometry, pMaterial);
        scene.add(pointCloud);

        // Metric Bounding Box around structure
        const boxGeo = new THREE.BoxGeometry(dimsData.length, dimsData.height, dimsData.width);
        const boxEdges = new THREE.EdgesGeometry(boxGeo);
        const boxLine = new THREE.LineSegments(boxEdges, new THREE.LineBasicMaterial({{
            color: 0x38bdf8, transparent: true, opacity: 0.4
        }}));
        boxLine.position.set(0, dimsData.height / 2, 0);
        boxLine.visible = false;
        scene.add(boxLine);

        // Trajectory Ribbon / Path
        const trajPoints = trajectoryData.map(p => new THREE.Vector3(p[0], p[1], p[2]));
        const trajGeo = new THREE.BufferGeometry().setFromPoints(trajPoints);
        const trajMat = new THREE.LineBasicMaterial({{ color: 0x00e5ff, linewidth: 2 }});
        const trajLine = new THREE.Line(trajGeo, trajMat);
        scene.add(trajLine);

        // Start & End Waypoint Markers
        if (trajPoints.length > 0) {{
            const startMarker = new THREE.Mesh(
                new THREE.SphereGeometry(0.12, 16, 16),
                new THREE.MeshBasicMaterial({{ color: 0x10b981 }})
            );
            startMarker.position.copy(trajPoints[0]);
            scene.add(startMarker);

            const endMarker = new THREE.Mesh(
                new THREE.SphereGeometry(0.12, 16, 16),
                new THREE.MeshBasicMaterial({{ color: 0xef4444 }})
            );
            endMarker.position.copy(trajPoints[trajPoints.length - 1]);
            scene.add(endMarker);
        }}

        // BlueROV2 3D Vehicle Representation
        const rovGroup = new THREE.Group();

        // Main Hull Chassis (Black/Yellow BlueROV2 body)
        const chassis = new THREE.Mesh(
            new THREE.BoxGeometry(0.46, 0.22, 0.34),
            new THREE.MeshStandardMaterial({{ color: 0x0f172a, roughness: 0.4 }})
        );
        rovGroup.add(chassis);

        // Buoyancy Foam Blocks (Yellow)
        const foam = new THREE.Mesh(
            new THREE.BoxGeometry(0.44, 0.08, 0.32),
            new THREE.MeshStandardMaterial({{ color: 0xf59e0b, roughness: 0.3 }})
        );
        foam.position.y = 0.14;
        rovGroup.add(foam);

        // Front Camera Dome (Cyan Glow)
        const camDome = new THREE.Mesh(
            new THREE.SphereGeometry(0.08, 16, 16),
            new THREE.MeshStandardMaterial({{ color: 0x00e5ff, emissive: 0x00e5ff, emissiveIntensity: 0.6 }})
        );
        camDome.position.set(0, 0.02, 0.22);
        rovGroup.add(camDome);

        // Front LED Floodlights
        const ledMat = new THREE.MeshBasicMaterial({{ color: 0xffffff }});
        const ledL = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.04), ledMat);
        ledL.rotation.x = Math.PI / 2;
        ledL.position.set(-0.16, 0.06, 0.20);
        const ledR = ledL.clone();
        ledR.position.x = 0.16;
        rovGroup.add(ledL);
        rovGroup.add(ledR);

        scene.add(rovGroup);

        // Ping1D Sonar Acoustic Beam Cone & Hit Target Marker
        const sonarConeGeo = new THREE.ConeGeometry(0.35, 1.0, 16, 1, true);
        sonarConeGeo.rotateX(-Math.PI / 2); // point forward
        sonarConeGeo.translate(0, 0, 0.5);
        const sonarConeMat = new THREE.MeshBasicMaterial({{
            color: 0x00e5ff,
            transparent: true,
            opacity: 0.22,
            wireframe: false,
            side: THREE.DoubleSide
        }});
        const sonarBeamMesh = new THREE.Mesh(sonarConeGeo, sonarConeMat);
        scene.add(sonarBeamMesh);

        // Acoustic Beam Core Line
        const sonarLineGeo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,0), new THREE.Vector3(0,0,1)]);
        const sonarLineMat = new THREE.LineBasicMaterial({{ color: 0x00e5ff, linewidth: 3 }});
        const sonarLine = new THREE.Line(sonarLineGeo, sonarLineMat);
        scene.add(sonarLine);

        // Acoustic Hit Point Indicator on Target Surface
        const hitMarker = new THREE.Mesh(
            new THREE.RingGeometry(0.08, 0.14, 16),
            new THREE.MeshBasicMaterial({{ color: 0x00e5ff, side: THREE.DoubleSide }})
        );
        scene.add(hitMarker);

        // State variables
        let currentWaypoint = 0;
        let isPlaying = false;
        let playInterval = null;
        let currentViewMode = 'orbit'; // 'orbit', 'fpv', 'topdown'
        let showSonar = true;
        let showTrack = true;
        let showBox = false;

        // Telemetry Update Function
        function updateWaypoint(idx) {{
            idx = Math.max(0, Math.min(idx, numWaypoints - 1));
            currentWaypoint = idx;
            const telem = telemetryData[idx];
            if (!telem) return;

            // 1. Move ROV to position
            const pos = telem.position;
            rovGroup.position.set(pos[0], pos[1], pos[2]);

            // Orient ROV according to forward vector and attitude
            const fwd = telem.forward_vec;
            const targetLook = new THREE.Vector3(pos[0] + fwd[0], pos[1] + fwd[1], pos[2] + fwd[2]);
            rovGroup.lookAt(targetLook);

            // 2. Update Ping1D Acoustic Beam
            const hit = telem.hit_point;
            const dist = telem.ping1d_distance_m;

            if (showSonar) {{
                sonarBeamMesh.visible = true;
                sonarLine.visible = true;
                hitMarker.visible = true;

                sonarBeamMesh.position.set(pos[0], pos[1], pos[2]);
                sonarBeamMesh.lookAt(hit[0], hit[1], hit[2]);
                sonarBeamMesh.scale.set(dist * 0.45, dist * 0.45, dist);

                sonarLine.geometry.setFromPoints([
                    new THREE.Vector3(pos[0], pos[1], pos[2]),
                    new THREE.Vector3(hit[0], hit[1], hit[2])
                ]);
                sonarLine.geometry.attributes.position.needsUpdate = true;

                hitMarker.position.set(hit[0], hit[1], hit[2]);
                hitMarker.lookAt(pos[0], pos[1], pos[2]);
            }} else {{
                sonarBeamMesh.visible = false;
                sonarLine.visible = false;
                hitMarker.visible = false;
            }}

            // 3. Update HUD readout elements
            document.getElementById('waypointBadge').textContent = `WP ${{idx + 1}}/${{numWaypoints}}`;
            document.getElementById('sonarDist').textContent = dist.toFixed(2);
            document.getElementById('sonarConf').textContent = `${{telem.ping1d_confidence_pct}}% CONF`;
            document.getElementById('bar30Depth').textContent = telem.bar30_depth_m.toFixed(2);
            document.getElementById('bar30Pressure').textContent = `${{telem.bar30_pressure_mbar.toFixed(0)}} mbar`;
            document.getElementById('imuRoll').textContent = `${{telem.imu.roll.toFixed(1)}}°`;
            document.getElementById('imuPitch').textContent = `${{telem.imu.pitch.toFixed(1)}}°`;
            document.getElementById('imuYaw').textContent = `${{telem.imu.yaw.toFixed(1)}}°`;

            document.getElementById('timelineSlider').value = idx;
            document.getElementById('timelineText').textContent = `${{idx + 1}}/${{numWaypoints}}`;

            // 4. Update Camera for FPV mode
            if (currentViewMode === 'fpv') {{
                camera.position.set(pos[0], pos[1] + 0.05, pos[2]);
                camera.lookAt(targetLook);
            }}
        }}

        // Play / Pause Animation Loop
        function togglePlay() {{
            isPlaying = !isPlaying;
            const btn = document.getElementById('btnPlayPause');
            if (isPlaying) {{
                btn.textContent = '⏸️ Jeda Misi';
                btn.classList.add('active');
                playInterval = setInterval(() => {{
                    let next = currentWaypoint + 1;
                    if (next >= numWaypoints) next = 0;
                    updateWaypoint(next);
                }}, 180);
            }} else {{
                btn.textContent = '▶️ Putar Misi';
                btn.classList.remove('active');
                clearInterval(playInterval);
            }}
        }}

        // Event Listeners
        document.getElementById('btnPlayPause').addEventListener('click', togglePlay);
        document.getElementById('btnReset').addEventListener('click', () => {{
            if (isPlaying) togglePlay();
            updateWaypoint(0);
        }});

        document.getElementById('timelineSlider').addEventListener('input', (e) => {{
            if (isPlaying) togglePlay();
            updateWaypoint(parseInt(e.target.value));
        }});

        document.getElementById('btnToggleSonar').addEventListener('click', (e) => {{
            showSonar = !showSonar;
            e.target.classList.toggle('active', showSonar);
            e.target.textContent = showSonar ? '🔊 Sinar Sonar: ON' : '🔊 Sinar Sonar: OFF';
            updateWaypoint(currentWaypoint);
        }});

        document.getElementById('btnToggleTrack').addEventListener('click', (e) => {{
            showTrack = !showTrack;
            e.target.classList.toggle('active', showTrack);
            e.target.textContent = showTrack ? '🛣️ Jalur Track: ON' : '🛣️ Jalur Track: OFF';
            trajLine.visible = showTrack;
        }});

        document.getElementById('btnToggleBox').addEventListener('click', (e) => {{
            showBox = !showBox;
            e.target.classList.toggle('active', showBox);
            boxLine.visible = showBox;
        }});

        // View Mode Switches
        const btnOrbit = document.getElementById('viewOrbit');
        const btnFPV = document.getElementById('viewFPV');
        const btnTopDown = document.getElementById('viewTopDown');
        const crosshair = document.getElementById('crosshair');

        btnOrbit.addEventListener('click', () => {{
            currentViewMode = 'orbit';
            controls.enabled = true;
            crosshair.style.display = 'none';
            btnOrbit.classList.add('active');
            btnFPV.classList.remove('active');
            btnTopDown.classList.remove('active');
            camera.position.set(6, 6, 9);
            controls.target.set(0, 1.5, 0);
        }});

        btnFPV.addEventListener('click', () => {{
            currentViewMode = 'fpv';
            controls.enabled = false;
            crosshair.style.display = 'block';
            btnFPV.classList.add('active');
            btnOrbit.classList.remove('active');
            btnTopDown.classList.remove('active');
            updateWaypoint(currentWaypoint);
        }});

        btnTopDown.addEventListener('click', () => {{
            currentViewMode = 'topdown';
            controls.enabled = true;
            crosshair.style.display = 'none';
            btnTopDown.classList.add('active');
            btnOrbit.classList.remove('active');
            btnFPV.classList.remove('active');
            camera.position.set(0, 14, 0.01);
            controls.target.set(0, 0, 0);
        }});

        // Initialize at Waypoint 0
        updateWaypoint(0);

        // Animation Loop
        function animate() {{
            requestAnimationFrame(animate);
            if (currentViewMode !== 'fpv') {{
                controls.update();
            }}
            // Subtle acoustic beam pulse
            if (showSonar) {{
                sonarConeMat.opacity = 0.20 + 0.06 * Math.sin(Date.now() * 0.008);
            }}
            renderer.render(scene, camera);
        }}
        animate();

        // Responsive Resize
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
    </script>
</body>
</html>
"""
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html)
        
    print(f"[OK] Viewer 3D interaktif siap di: {output_html_path}")

if __name__ == "__main__":
    json_in = r"c:\remote_ROV\metric_reconstruction_data.json"
    html_out = r"c:\remote_ROV\view_metric_3d_mapping.html"
    generate_metric_viewer(json_in, html_out)
