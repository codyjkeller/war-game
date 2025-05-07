<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WW2 Trench Defense - Save/Load</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js"></script>
    <style>
        body {
            font-family: 'Inter', sans-serif; display: flex; flex-direction: column;
            justify-content: center; align-items: center; min-height: 100vh;
            background-color: #4B3A2A; margin: 0; overflow: hidden; color: #e2e8f0;
        }
        canvas {
            display: block; border: 2px solid #5a4a3a; border-radius: 0.5rem;
            max-width: 100%; max-height: 80vh;
            aspect-ratio: 16 / 10;
            background-color: #8B8378; /* Fallback */
            position: relative; cursor: crosshair;
        }
        .canvas-container {
             position: relative; width: 95%; max-width: 1100px;
             display: flex; justify-content: center; align-items: center;
        }
        .control-button, .game-action-button { /* Combined styles for consistency */
            background-color: #5a4a3a; color: #e2e8f0; border: 1px solid #4a3a2a;
            padding: 0.5rem 1rem; margin: 0 0.15rem; border-radius: 0.5rem; cursor: pointer;
            font-weight: 600; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            transition: background-color 0.2s ease, transform 0.1s ease;
            font-size: 0.8rem;
        }
        .control-button:active, .game-action-button:active { background-color: #4a3a2a; transform: scale(0.95); }
        .game-action-button { margin-top: 0.5rem; } /* Specific margin for save/load buttons */

        @media (max-width: 768px) { #keyboard-instructions { display: none; } }
        @media (min-width: 769px) { #touch-controls { display: none; } }

        #message-box, #pause-menu, #deployment-overlay, #upgrade-menu, #skill-tree-menu { /* Combined overlay styles */
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background-color: rgba(74, 58, 42, 0.95); color: #e2e8f0;
            padding: 1.5rem; border-radius: 0.75rem; text-align: center;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4); z-index: 100;
            display: none; border: 1px solid #9a7a5a; min-width: 320px; max-width: 90%;
        }
        #message-box h2, #pause-menu h2, #deployment-overlay h2, #upgrade-menu h2, #skill-tree-menu h2 { font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem; }
        #message-box p, #pause-menu p, #deployment-overlay p, #upgrade-menu p, #skill-tree-menu p { margin-bottom: 1rem; }
        #message-box button, #pause-menu button, #upgrade-menu button, #deployment-overlay button, #skill-tree-menu button {
             background-color: #6a7a4a; color: white; border: none;
             padding: 0.6rem 1.2rem; border-radius: 0.5rem; cursor: pointer;
             font-weight: 600; transition: background-color 0.2s ease;
             display: block; width: 100%; margin-top: 0.75rem;
        }
        #message-box button:hover, #pause-menu button:hover, #upgrade-menu button:hover, #deployment-overlay button:hover, #skill-tree-menu button:hover { background-color: #5a6a3a; }
        #upgrade-menu button:disabled, #skill-tree-menu button:disabled { background-color: #555; cursor: not-allowed; }

        #upgrade-menu .upgrade-option, #skill-tree-menu .skill-option { margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; }
        #upgrade-menu .upgrade-option span, #skill-tree-menu .skill-option span { font-size: 0.9rem; }
        #upgrade-menu .upgrade-cost, #skill-tree-menu .skill-cost { font-weight: bold; color: #f6e05e; margin-left: 10px; }
        #upgrade-menu .upgrade-level, #skill-tree-menu .skill-level { font-size: 0.8rem; color: #a0aec0; margin-left: 5px; }


        #wave-notification {
            position: absolute; top: 30%; left: 50%; transform: translateX(-50%);
            background-color: rgba(0, 0, 0, 0.7); color: white; padding: 1rem 2rem;
            border-radius: 0.5rem; font-size: 1.8rem; font-weight: bold;
            z-index: 50; display: none; text-align: center;
        }
        #powerup-timer {
             font-weight: bold; color: #f6e05e; margin-left: 1rem; display: none;
        }
        .ui-icon {
            display: inline-block; margin-right: 0.25rem; font-size: 1.1em; vertical-align: middle;
        }
        .cooldown-indicator-bg {
            display: inline-block; width: 40px; height: 8px; background-color: #555;
            border-radius: 4px; margin-left: 5px; vertical-align: middle; overflow: hidden;
        }
        .cooldown-indicator-bar {
            height: 100%; background-color: #f6e05e; width: 0%; border-radius: 4px; transition: width 0.1s linear;
        }
        #adrenaline-overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(0, 150, 255, 0.15);
            z-index: 40; display: none; pointer-events: none;
        }
        #ability-list {
            margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #9a7a5a;
            text-align: left; font-size: 0.9rem;
        }
        #ability-list h3 { font-weight: bold; margin-bottom: 0.5rem; text-align: center; }
        #ability-list div { margin-bottom: 0.3rem; }
         #ability-list span { display: inline-block; min-width: 80px; }
         #initial-load-button-container { margin-top: 1rem; }
    </style>
</head>
<body>

    <div id="ui" class="my-2 text-lg font-semibold flex flex-wrap justify-center gap-x-6 gap-y-1"> <span><span class="ui-icon">🌊</span> Wave: <span id="wave">1</span></span>
        <span><span class="ui-icon">⭐</span> Score: <span id="score">0</span></span>
        <span><span class="ui-icon">❤️</span> Health: <span id="health">100</span></span>
        <span><span class="ui-icon">🧱</span> Trench: <span id="trench-health">100</span></span>
        <span><span class="ui-icon">💣</span> G: <span id="grenades">3</span><span class="cooldown-indicator-bg"><div id="grenade-cooldown-bar" class="cooldown-indicator-bar"></div></span></span>
        <span><span class="ui-icon">🚀</span> R: <span id="rockets">1</span><span class="cooldown-indicator-bg"><div id="rocket-cooldown-bar" class="cooldown-indicator-bar"></div></span></span>
        <span><span class="ui-icon">🧑‍🤝‍🧑</span> Allies: <span id="allies">0</span>/<span id="max-allies">0</span></span>
        <span><span class="ui-icon">🔧</span> F: <span class="cooldown-indicator-bg"><div id="repair-cooldown-bar" class="cooldown-indicator-bar"></div></span></span>
        <span><span class="ui-icon">✈️</span> A: <span class="cooldown-indicator-bg"><div id="airstrike-cooldown-bar" class="cooldown-indicator-bar"></div></span></span>
        <span><span class="ui-icon">⚡</span> D: <span class="cooldown-indicator-bg"><div id="adrenaline-cooldown-bar" class="cooldown-indicator-bar"></div></span></span> <span id="powerup-timer"><span id="powerup-type-icon"></span><span id="powerup-type"></span> <span id="powerup-time-left">0</span>s</span>
    </div>

    <div class="canvas-container"> <canvas id="gameCanvas"></canvas>
        <div id="adrenaline-overlay"></div> <div id="wave-notification">Wave 1 Starting!</div>
        <div id="message-box">
            <h2 id="message-title">Position Overrun!</h2>
            <p id="message-text">Your final score is 0.</p>
            <button id="restart-button">Try Again</button>
        </div>
        <div id="pause-menu">
             <h2>Game Paused</h2>
             <button id="resume-button">Resume</button>
             <button id="save-game-button" class="game-action-button">Save Game</button>
             <button id="load-game-button" class="game-action-button">Load Game</button>
             <button id="restart-pause-button" class="game-action-button">Restart</button>
             <div id="ability-list">
                 <h3>Abilities</h3>
                 <div><span>[G] Grenade:</span> Area explosion.</div>
                 <div><span>[R] Rocket:</span> High damage projectile.</div>
                 <div><span>[F] Repair:</span> Restore trench health.</div>
                 <div><span>[A] Airstrike:</span> Bombard the battlefield.</div>
                 <div><span>[D] Adrenaline:</span> Slow enemies, faster fire.</div> </div>
        </div>
         <div id="deployment-overlay">
             <h2>Deployment Phase</h2>
             <p>Place Barbed Wire!</p>
             <p>Remaining: <span id="deployments-left">0</span></p>
             <button id="finish-deployment-button" style="background-color: #4a5568; margin-top: 1rem;">Finish Deployment</button> </div>
         <div id="upgrade-menu">
              <h2>Wave Complete! Upgrades Available</h2>
              <p>Score: <span id="upgrade-score">0</span></p>
              <div class="upgrade-option">
                  <span>Fire Rate <span class="upgrade-level" id="firerate-level">(Lvl 1)</span></span>
                  <button id="upgrade-firerate" data-upgrade="fireRate">Cost: <span class="upgrade-cost" id="firerate-cost">100</span></button>
              </div>
              <div class="upgrade-option">
                  <span>Move Speed <span class="upgrade-level" id="movespeed-level">(Lvl 1)</span></span>
                  <button id="upgrade-movespeed" data-upgrade="moveSpeed">Cost: <span class="upgrade-cost" id="movespeed-cost">150</span></button>
              </div>
              <div class="upgrade-option">
                   <span>Grenade Cap <span class="upgrade-level" id="grenadecap-level">(Lvl 1)</span></span>
                   <button id="upgrade-grenadecap" data-upgrade="grenadeCap">Cost: <span class="upgrade-cost" id="grenadecap-cost">200</span></button>
               </div>
               <div class="upgrade-option">
                   <span>Rocket Cap <span class="upgrade-level" id="rocketcap-level">(Lvl 1)</span></span>
                   <button id="upgrade-rocketcap" data-upgrade="rocketCap">Cost: <span class="upgrade-cost" id="rocketcap-cost">300</span></button>
               </div>
               <div class="upgrade-option">
                   <span>Trench Repair <span class="upgrade-level" id="trenchrepair-level">(Lvl 1)</span></span>
                   <button id="upgrade-trenchrepair" data-upgrade="trenchRepair">Cost: <span class="upgrade-cost" id="trenchrepair-cost">120</span></button>
               </div>
              <button id="skill-tree-button" style="background-color: #D69E2E; margin-top: 1rem;">Skill Tree (<span id="skill-points-display">0</span> SP)</button>
              <button id="continue-button" style="background-color: #38a169; margin-top: 1.5rem;">Start Next Wave</button>
         </div>
         <div id="skill-tree-menu">
            <h2>Skill Tree</h2>
            <p>Skill Points: <span id="skill-points-available">0</span></p>
            <div class="skill-option">
                <span>Trench Resilience <span class="skill-level" id="trenchresilience-level">(Lvl 0)</span></span>
                <button id="skill-trenchresilience" data-skill="trenchResilience">Cost: <span class="skill-cost">1 SP</span></button>
            </div>
            <div class="skill-option">
                <span>Combat Medic <span class="skill-level" id="combatmedic-level">(Lvl 0)</span></span>
                <button id="skill-combatmedic" data-skill="combatMedic">Cost: <span class="skill-cost">1 SP</span></button>
            </div>
            <div class="skill-option">
                <span>Explosives Expert <span class="skill-level" id="explosivesexpert-level">(Lvl 0)</span></span>
                <button id="skill-explosivesexpert" data-skill="explosivesExpert">Cost: <span class="skill-cost">1 SP</span></button>
            </div>
             <div class="skill-option">
                <span>Rapid Deployment <span class="skill-level" id="rapiddeployment-level">(Lvl 0)</span></span>
                <button id="skill-rapiddeployment" data-skill="rapidDeployment">Cost: <span class="skill-cost">1 SP</span></button>
            </div>
            <button id="close-skill-tree-button" style="background-color: #718096; margin-top: 1.5rem;">Close</button>
        </div>
    </div>

    <div id="initial-load-button-container" class="flex justify-center">
        </div>

    <div id="keyboard-instructions" class="mt-2 text-sm text-gray-400">
        Arrows: Move, Space: Shoot, G: Nade, R: Rockt, F: Repair, A: Airstrike, D: Adren, P: Pause </div>

    <div id="touch-controls" class="mt-2 flex justify-center w-full px-1">
        <button id="left-btn" class="control-button">Left</button>
        <button id="shoot-btn" class="control-button">Shoot</button>
        <button id="grenade-btn" class="control-button">Nade</button>
        <button id="rocket-btn" class="control-button">Rockt</button>
        <button id="repair-btn" class="control-button">Repair</button>
        <button id="airstrike-btn" class="control-button">Air</button>
        <button id="adrenaline-btn" class="control-button">Adren</button>
        <button id="right-btn" class="control-button">Right</button>
        <button id="pause-btn" class="control-button">Pause</button>
    </div>


    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreElement = document.getElementById('score');
        const healthElement = document.getElementById('health');
        const trenchHealthElement = document.getElementById('trench-health');
        const waveElement = document.getElementById('wave');
        const grenadeElement = document.getElementById('grenades');
        const rocketElement = document.getElementById('rockets');
        const alliesElement = document.getElementById('allies');
        const maxAlliesElement = document.getElementById('max-allies');
        const powerupTimerElement = document.getElementById('powerup-timer');
        const powerupTypeElement = document.getElementById('powerup-type');
        const powerupTypeIconElement = document.getElementById('powerup-type-icon');
        const powerupTimeLeftElement = document.getElementById('powerup-time-left');
        const waveNotificationElement = document.getElementById('wave-notification');
        const messageBox = document.getElementById('message-box');
        const messageTitle = document.getElementById('message-title');
        const messageText = document.getElementById('message-text');
        const restartButton = document.getElementById('restart-button');
        const pauseMenu = document.getElementById('pause-menu');
        const resumeButton = document.getElementById('resume-button');
        const restartPauseButton = document.getElementById('restart-pause-button');
        const pauseButton = document.getElementById('pause-btn');
        const deploymentOverlay = document.getElementById('deployment-overlay');
        const deploymentsLeftElement = document.getElementById('deployments-left');
        const finishDeploymentButton = document.getElementById('finish-deployment-button');
        const upgradeMenu = document.getElementById('upgrade-menu');
        const upgradeScoreElement = document.getElementById('upgrade-score');
        const continueButton = document.getElementById('continue-button');
        const grenadeCooldownBar = document.getElementById('grenade-cooldown-bar');
        const rocketCooldownBar = document.getElementById('rocket-cooldown-bar');
        const repairCooldownBar = document.getElementById('repair-cooldown-bar');
        const airstrikeCooldownBar = document.getElementById('airstrike-cooldown-bar');
        const adrenalineCooldownBar = document.getElementById('adrenaline-cooldown-bar');
        const adrenalineOverlay = document.getElementById('adrenaline-overlay');
        // Skill Tree UI
        const skillTreeButton = document.getElementById('skill-tree-button');
        const skillPointsDisplay = document.getElementById('skill-points-display');
        const skillTreeMenu = document.getElementById('skill-tree-menu');
        const skillPointsAvailableElement = document.getElementById('skill-points-available');
        const closeSkillTreeButton = document.getElementById('close-skill-tree-button');
        // Save/Load Buttons
        const saveGameButton = document.getElementById('save-game-button');
        const loadGameButton = document.getElementById('load-game-button');
        const initialLoadButtonContainer = document.getElementById('initial-load-button-container');


        // --- Game State ---
        let score = 0; let playerHealth = 100; let trenchHealth = 100; let maxTrenchHealth = 100;
        let gameOver = false; let gameRunning = true;
        let isPaused = false; let isDeploymentPhase = false; let isUpgradePhase = false; let isSkillTreePhase = false;
        let animationFrameId; let toneStarted = false; let currentWave = 0;
        let enemiesToSpawnThisWave = 0; let enemiesSpawnedThisWave = 0; let enemiesKilledThisWave = 0;
        let waveTransitionCounter = 0; const waveTransitionTime = 180;
        let grenadeCount = 3; let maxGrenades = 3; let grenadeCooldownTime = 60; let grenadeCooldownCounter = 0;
        let rocketCount = 1; let maxRockets = 1; let rocketCooldownTime = 180; let rocketCooldownCounter = 0;
        let screenShakeMagnitude = 0; let screenShakeDuration = 0;
        let playerPowerUp = { type: null, timer: 0 };
        let deploymentsAvailable = 0; let deploymentPlacementPreview = null;
        let mousePos = { x: 0, y: 0 };
        let lastSoundTriggerTime = 0; const soundTimeOffset = 0.001;
        let trenchRepairRate = 0.01;
        // Ability States
        let trenchRepairAbilityCooldownTime = 600; let trenchRepairAbilityCooldownCounter = 0; const trenchRepairAbilityAmount = 20;
        let airstrikeAbilityCooldownTime = 1800; let airstrikeAbilityCooldownCounter = 0; let airstrikeActive = false; let airstrikeTimer = 0; const airstrikeDuration = 120; const airstrikesPerCall = 8;
        let adrenalineAbilityCooldownTime = 1200; let adrenalineAbilityCooldownCounter = 0; let adrenalineActive = false; let adrenalineTimer = 0; const adrenalineDuration = 300;
        const adrenalineSlowFactor = 0.4;
        let isMiniBossActive = false;

        // Skill Tree State
        let skillPoints = 0;
        let skillLevels = {
            trenchResilience: 0,
            combatMedic: 0,
            explosivesExpert: 0,
            rapidDeployment: 0
        };
        const skillMaxLevel = 5;

        // --- Upgrade State ---
        let upgradeLevels = { fireRate: 1, moveSpeed: 1, grenadeCap: 1, rocketCap: 1, trenchRepair: 1 };
        const upgradeBaseCosts = { fireRate: 100, moveSpeed: 150, grenadeCap: 200, rocketCap: 300, trenchRepair: 120 };
        const upgradeCostMultiplier = 1.5;

        // --- Game Settings ---
        const trenchHeight = 60;
        let backTrenchY = 0;
        const basePlayerSpeed = 12; let currentPlayerSpeed = basePlayerSpeed;
        const playerWidth = 30; const playerHeight = 40;
        const bulletWidth = 3; const bulletHeight = 10; const bulletSpeed = 10;
        const enemyWidth = 30; const enemyHeight = 40; const baseEnemySpeed = 0.8;
        const baseEnemySpawnRate = 120; let currentEnemySpawnRate = baseEnemySpawnRate; let enemySpawnCounter = 0;
        let baseBulletDamage = 10; let currentBulletDamage = baseBulletDamage;
        const npcBulletDamage = 8; const enemyBulletDamage = 5;
        const enemyCollisionDamage = 25; const enemyTrenchDamage = 5;
        const baseShootCooldownTime = 4; let currentShootCooldownTime = baseShootCooldownTime; let shootCooldownCounter = 0;
        const obstacleSlowFactor = 0.4; const barbedWireColor = '#404040';
        const deploymentWireWidth = 50; const deploymentWireHeight = 20;
        const npcColor = '#6a7a4a'; const npcGunColor = '#555555'; const npcHealth = 100; const maxFriendlyNPCs = 4; const npcWidth = 28; const npcHeight = 38;
        const npcShootCooldownBase = 120; const npcShootCooldownVariance = 60; const npcMoveCooldown = 180; const npcMoveRange = 40;
        const npcHitFlashDuration = 6;
        const officerBuffRadius = 100; const officerFireRateBuff = 0.8;
        const bloodParticleColor = 'rgba(200, 0, 0, 0.7)'; const particleGravity = 0.1; const particleLife = 30;
        const debrisParticleColor = 'rgba(100, 80, 60, 0.7)'; const sparkParticleColor = 'rgba(255, 255, 100, 0.9)';
        const enemyBodyColor = '#6b5335'; const enemyHeadColor = '#f0d8b8';
        const enemyHelmetColor = '#556B2F'; const enemyGunColor = '#4a4a4a';
        const toughEnemyColor = '#8B4513'; const fastEnemyColor = '#A0522D';
        const shooterEnemyColor = '#708090'; const mortarEnemyColor = '#465945'; const shieldEnemyColor = '#666';
        const grenadierEnemyColor = '#B8860B'; const sniperEnemyColor = '#483D8B';
        const medicColor = '#D3D3D3'; const commanderColor = '#FFD700';
        const muzzleFlashColor = 'rgba(255, 223, 0, 0.8)'; const muzzleFlashLife = 3;
        const grenadeRadius = 50; let baseGrenadeDamage = 50; let currentGrenadeDamage = baseGrenadeDamage; const grenadeFuseTime = 30;
        const grenadeThrowSpeed = 8;
        const explosionColor = 'rgba(255, 100, 0, 0.7)'; const explosionLife = 15;
        const baseScreenShakeMagnitude = 4; const baseScreenShakeDuration = 10;
        const powerUpDropChance = 0.15; const reinforcementDropChance = 0.05; const healthDropChance = 0.08; const shotgunDropChance = 0.1;
        const powerUpDuration = 600; const rapidFireCooldown = 1; const shotgunSpread = Math.PI / 12; const shotgunPellets = 5; const healthPackAmount = 25;
        const mortarShellSpeed = 3; const mortarRadius = 30; const mortarDamage = 30;
        const mortarTargetMarkerColor = 'rgba(255, 0, 0, 0.5)';
        const deploymentsPerPhase = 3;
        const rocketWidth = 6; const rocketHeight = 15; const rocketSpeed = 12; const rocketRadius = 60; let baseRocketDamage = 100; let currentRocketDamage = baseRocketDamage;
        const rocketFuseTime = 50;
        const ambientNpcColor = '#8FBC8F'; const ambientNpcSpeed = 0.3;
        const officerCapColor = '#B8860B';
        const cloudColor = 'rgba(255, 255, 255, 0.6)'; const numClouds = 5;
        const cloudMinSpeed = 0.1; const cloudMaxSpeed = 0.4; const cloudScrollFactor = 0.3;
        const enemyAnimSpeed = 10; const enemyArmSwingAngle = Math.PI / 8;
        const hitMarkerColor = 'rgba(255, 255, 255, 0.8)'; const hitMarkerSize = 8; const hitMarkerLife = 10;
        const medicHealAmount = 15; const medicHealRadius = 60; const medicHealCooldown = 150;
        const commanderBuffRadius = 70; const commanderSpeedBuff = 1.3;
        const grenadierGrenadeFuse = 70; const grenadierGrenadeRadius = 40; const grenadierGrenadeDamage = 30;
        const sniperShotDamage = 40; const sniperAimTime = 150; const sniperTargetLineColor = 'rgba(255, 0, 0, 0.3)';
        // Mini-Boss: Armored Car
        const armoredCarWidth = 60; const armoredCarHeight = 50; const armoredCarColor = '#404040'; const armoredCarTurretColor = '#505050';
        const armoredCarHealth = 500; const armoredCarSpeed = 0.3; const armoredCarStopYFactor = 0.5;
        const cannonballRadius = 8; const cannonballSpeed = 4; const cannonballDamage = 35; const armoredCarShootCooldown = 180;


        // --- Game Objects ---
        let player = { x: 0, y: 0, width: playerWidth, height: playerHeight, color: '#5a6a3a', gunColor: '#4a4a4a', gunWidth: 5, gunLength: 25, dx: 0 };
        let bullets = []; let npcBullets = []; let enemyBullets = []; let mortarShells = []; let rockets = []; let cannonballs = [];
        let enemies = []; let obstacles = []; let friendlyNPCs = []; let ambientNPCs = []; let clouds = [];
        let particles = []; let muzzleFlashes = []; let grenades = []; let explosions = []; let powerUps = []; let hitMarkers = [];
        let airstrikeMarkers = [];

        // --- Sound Effects (Tone.js) ---
        const shootSound = new Tone.NoiseSynth({ noise: { type: 'white' }, envelope: { attack: 0.001, decay: 0.05, sustain: 0, release: 0.05 } }).toDestination(); shootSound.volume.value = -20;
        const shotgunSound = new Tone.NoiseSynth({ noise: { type: 'pink' }, envelope: { attack: 0.005, decay: 0.15, sustain: 0, release: 0.1 } }).toDestination(); shotgunSound.volume.value = -15;
        const npcShootSound = new Tone.NoiseSynth({ noise: { type: 'brown' }, envelope: { attack: 0.002, decay: 0.06, sustain: 0, release: 0.06 } }).toDestination(); npcShootSound.volume.value = -25;
        const enemyShootSound = new Tone.NoiseSynth({ noise: { type: 'pink' }, envelope: { attack: 0.005, decay: 0.08, sustain: 0, release: 0.08 } }).toDestination(); enemyShootSound.volume.value = -23;
        const explosionSound = new Tone.MembraneSynth({ pitchDecay: 0.05, octaves: 10, oscillator: { type: 'sine' }, envelope: { attack: 0.001, decay: 0.4, sustain: 0.01, release: 1.4, attackCurve: 'exponential' } }).toDestination(); explosionSound.volume.value = -10;
        const powerUpSound = new Tone.Synth({ oscillator: { type: "sine" }, envelope: { attack: 0.01, decay: 0.1, sustain: 0.2, release: 0.3 } }).toDestination(); powerUpSound.volume.value = -15;
        const mortarLaunchSound = new Tone.Synth({ oscillator: { type: "triangle" }, envelope: { attack: 0.1, decay: 0.2, sustain: 0.1, release: 0.5 } }).toDestination(); mortarLaunchSound.volume.value = -18;
        const reinforcementSound = new Tone.Synth({ oscillator: { type: "square" }, envelope: { attack: 0.02, decay: 0.1, sustain: 0.3, release: 0.4 } }).toDestination(); reinforcementSound.volume.value = -12;
        const placeWireSound = new Tone.MetalSynth({ frequency: 100, envelope: { attack: 0.01, decay: 0.1, release: 0.1 }, harmonicity: 3.1, modulationIndex: 16, resonance: 2000, octaves: 0.5 }).toDestination(); placeWireSound.volume.value = -15;
        const rocketLaunchSound = new Tone.Synth({ oscillator: { type: "sawtooth" }, envelope: { attack: 0.05, decay: 0.3, sustain: 0.1, release: 0.8 }, filter: { type: "lowpass", frequency: 1000, rolloff: -12 }, filterEnvelope: { attack: 0.1, decay: 0.2, sustain: 0.5, release: 0.6, baseFrequency: 200, octaves: 3 } }).toDestination(); rocketLaunchSound.volume.value = -8;
        const healthSound = new Tone.Synth({ oscillator: { type: "triangle" }, envelope: { attack: 0.01, decay: 0.2, sustain: 0.1, release: 0.2 } }).toDestination(); healthSound.volume.value = -14;
        const trenchDamageSound = new Tone.NoiseSynth({ noise: { type: 'brown' }, envelope: { attack: 0.01, decay: 0.2, sustain: 0, release: 0.1 } }).toDestination(); trenchDamageSound.volume.value = -15;
        const enemyDeathSound = new Tone.Player({ url: "https://tonejs.github.io/audio/berklee/gong_1.mp3", autostart: false }).toDestination(); enemyDeathSound.volume.value = -25; // Placeholder
        const playerKillSound = new Tone.Player({ url: "https://tonejs.github.io/audio/berklee/gong_1.mp3", autostart: false }).toDestination(); playerKillSound.volume.value = -18; // Kill confirmation sound (Placeholder)
        const medicHealSound = new Tone.Synth({ oscillator: { type: "sine" }, envelope: { attack: 0.1, decay: 0.1, sustain: 0.1, release: 0.2 } }).toDestination(); medicHealSound.volume.value = -18;
        const commanderBuffSound = new Tone.Synth({ oscillator: { type: "square" }, envelope: { attack: 0.01, decay: 0.3, sustain: 0, release: 0.1 } }).toDestination(); commanderBuffSound.volume.value = -20;
        const upgradeSound = new Tone.Synth({ oscillator: { type: "square" }, frequency: "A4", envelope: { attack: 0.01, decay: 0.05, sustain: 0, release: 0.1 } }).toDestination(); upgradeSound.volume.value = -15;
        const repairSound = new Tone.Synth({ oscillator: { type: "sine" }, frequency: "E4", envelope: { attack: 0.01, decay: 0.1, sustain: 0.05, release: 0.1 } }).toDestination(); repairSound.volume.value = -16;
        const airstrikeWarnSound = new Tone.Synth({ oscillator: { type: "sine" }, frequency: "B5", envelope: { attack: 0.01, decay: 0.5, sustain: 0, release: 0.1 } }).toDestination(); airstrikeWarnSound.volume.value = -10;
        const adrenalineSound = new Tone.Synth({ oscillator: { type: "pulse", width: 0.4 }, frequency: "G#4", envelope: { attack: 0.02, decay: 0.3, sustain: 0.1, release: 0.4 } }).toDestination(); adrenalineSound.volume.value = -12;
        const skillUnlockSound = new Tone.Synth({ oscillator: { type: "triangle" }, frequency: "C5", envelope: { attack: 0.01, decay: 0.2, sustain: 0, release: 0.1 } }).toDestination(); skillUnlockSound.volume.value = -14;
        const enemyGrenadeSound = new Tone.NoiseSynth({ noise: { type: 'white' }, envelope: { attack: 0.001, decay: 0.08, sustain: 0, release: 0.08 } }).toDestination(); enemyGrenadeSound.volume.value = -22;
        const sniperShotSound = new Tone.Synth({ oscillator: { type: "sawtooth" }, frequency: "A2", envelope: { attack: 0.01, decay: 0.3, sustain: 0, release: 0.2 }, filter: { type: "lowpass", Q: 5, frequency: 800 }, filterEnvelope: { attack: 0.02, decay: 0.1, baseFrequency: 200, octaves: 2 } }).toDestination(); sniperShotSound.volume.value = -12;
        const cannonFireSound = new Tone.MembraneSynth({ pitchDecay: 0.1, octaves: 5, oscillator: { type: 'triangle' }, envelope: { attack: 0.01, decay: 0.5, sustain: 0.02, release: 1.0 } }).toDestination(); cannonFireSound.volume.value = -8;


        // Helper function to get the next valid sound trigger time
        function getNextSoundTime() { const now = Tone.now(); const nextTime = Math.max(now, lastSoundTriggerTime + soundTimeOffset); lastSoundTriggerTime = nextTime; return nextTime; }

        // --- Input Handling ---
        const keys = { ArrowLeft: false, ArrowRight: false, /*KeyW: false, KeyS: false,*/ Space: false, KeyG: false, KeyP: false, KeyR: false, KeyF: false, KeyA: false, KeyD: false }; // Removed W/S, Changed S to D
        document.addEventListener('keydown', (e) => {
            if (gameOver || isSkillTreePhase) return; // Prevent actions if skill tree is open
            if (e.code === 'ArrowLeft') keys.ArrowLeft = true; if (e.code === 'ArrowRight') keys.ArrowRight = true;
            // if (e.code === 'KeyW') keys.KeyW = true; if (e.code === 'KeyS') keys.KeyS = true; // Removed
            if (e.code === 'Space') keys.Space = true; if (e.code === 'KeyG') keys.KeyG = true; if (e.code === 'KeyP') keys.KeyP = true; if (e.code === 'KeyR') keys.KeyR = true;
            if (e.code === 'KeyF') keys.KeyF = true; if (e.code === 'KeyA') keys.KeyA = true; if (e.code === 'KeyD') keys.KeyD = true; // Changed S to D

            if (!toneStarted && (e.code === 'ArrowLeft' || e.code === 'ArrowRight' || e.code === 'Space' || e.code === 'KeyG' || e.code === 'KeyP' || e.code === 'KeyR' || e.code === 'KeyF' || e.code === 'KeyA' || e.code === 'KeyD' /*|| e.code === 'KeyW' || e.code === 'KeyS'*/)) { Tone.start().then(() => { toneStarted = true; lastSoundTriggerTime = Tone.now(); console.log("Audio Context Started (Keyboard)"); }).catch(err => console.error("Tone.start error:", err)); }
            if (keys.KeyP) { togglePause(); keys.KeyP = false; }
            if (!isPaused && !isDeploymentPhase && !isUpgradePhase) {
                 if (keys.KeyG && grenadeCooldownCounter <= 0 && grenadeCount > 0) { throwGrenade(); keys.KeyG = false; }
                 if (keys.KeyR && rocketCooldownCounter <= 0 && rocketCount > 0) { shootRocket(); keys.KeyR = false; }
                 if (keys.KeyF && trenchRepairAbilityCooldownCounter <= 0) { activateTrenchRepair(); keys.KeyF = false; }
                 if (keys.KeyA && airstrikeAbilityCooldownCounter <= 0) { activateAirstrike(); keys.KeyA = false; }
                 if (keys.KeyD && adrenalineAbilityCooldownCounter <= 0) { activateAdrenaline(); keys.KeyD = false; } // Changed S to D
            }
        });
        document.addEventListener('keyup', (e) => { if (e.code === 'ArrowLeft') keys.ArrowLeft = false; if (e.code === 'ArrowRight') keys.ArrowRight = false; if (e.code === 'Space') keys.Space = false; /*if (e.code === 'KeyW') keys.KeyW = false; if (e.code === 'KeyS') keys.KeyS = false;*/ });

        const leftBtn = document.getElementById('left-btn'); const rightBtn = document.getElementById('right-btn'); const shootBtn = document.getElementById('shoot-btn'); const grenadeBtn = document.getElementById('grenade-btn'); const rocketBtn = document.getElementById('rocket-btn');
        const repairBtn = document.getElementById('repair-btn'); const airstrikeBtn = document.getElementById('airstrike-btn'); const adrenalineBtn = document.getElementById('adrenaline-btn');
        // Removed upBtn, downBtn
        let touchLeft = false, touchRight = false, touchShoot = false, touchGrenade = false, touchRocket = false, touchRepair = false, touchAirstrike = false, touchAdrenaline = false; // Removed touchUp, touchDown

        function handleTouchStart(e, action) {
             e.preventDefault(); if (!toneStarted) { Tone.start().then(() => { toneStarted = true; lastSoundTriggerTime = Tone.now(); console.log("Audio Context Started (Touch)"); }).catch(err => console.error("Tone.start error:", err)); }
             if (isPaused || gameOver || isDeploymentPhase || isUpgradePhase || isSkillTreePhase) return;
             if(action === 'left') touchLeft = true; if(action === 'right') touchRight = true; if(action === 'shoot') touchShoot = true;
             if(action === 'grenade') { touchGrenade = true; if (grenadeCooldownCounter <= 0 && grenadeCount > 0) { throwGrenade(); } }
             if(action === 'rocket') { touchRocket = true; if (rocketCooldownCounter <= 0 && rocketCount > 0) { shootRocket(); } }
             if(action === 'repair') { touchRepair = true; if (trenchRepairAbilityCooldownCounter <= 0) { activateTrenchRepair(); } }
             if(action === 'airstrike') { touchAirstrike = true; if (airstrikeAbilityCooldownCounter <= 0) { activateAirstrike(); } }
             if(action === 'adrenaline') { touchAdrenaline = true; if (adrenalineAbilityCooldownCounter <= 0) { activateAdrenaline(); } }
        }
        function handleTouchEnd(e, action) { e.preventDefault(); if(action === 'left') touchLeft = false; if(action === 'right') touchRight = false; if(action === 'shoot') touchShoot = false; if(action === 'grenade') touchGrenade = false; if(action === 'rocket') touchRocket = false; if(action === 'repair') touchRepair = false; if(action === 'airstrike') touchAirstrike = false; if(action === 'adrenaline') touchAdrenaline = false; }

        leftBtn.addEventListener('touchstart', (e) => handleTouchStart(e, 'left'), { passive: false }); leftBtn.addEventListener('touchend', (e) => handleTouchEnd(e, 'left'));
        rightBtn.addEventListener('touchstart', (e) => handleTouchStart(e, 'right'), { passive: false }); rightBtn.addEventListener('touchend', (e) => handleTouchEnd(e, 'right'));
        shootBtn.addEventListener('touchstart', (e) => handleTouchStart(e, 'shoot'), { passive: false }); shootBtn.addEventListener('touchend', (e) => handleTouchEnd(e, 'shoot'));
        grenadeBtn.addEventListener('touchstart', (e) => handleTouchStart(e, 'grenade'), { passive: false }); grenadeBtn.addEventListener('touchend', (e) => handleTouchEnd(e, 'grenade'));
        rocketBtn.addEventListener('touchstart', (e) => handleTouchStart(e, 'rocket'), { passive: false }); rocketBtn.addEventListener('touchend', (e) => handleTouchEnd(e, 'rocket'));
        repairBtn.addEventListener('touchstart', (e) => handleTouchStart(e, 'repair'), { passive: false }); repairBtn.addEventListener('touchend', (e) => handleTouchEnd(e, 'repair'));
        airstrikeBtn.addEventListener('touchstart', (e) => handleTouchStart(e, 'airstrike'), { passive: false }); airstrikeBtn.addEventListener('touchend', (e) => handleTouchEnd(e, 'airstrike'));
        adrenalineBtn.addEventListener('touchstart', (e) => handleTouchStart(e, 'adrenaline'), { passive: false }); adrenalineBtn.addEventListener('touchend', (e) => handleTouchEnd(e, 'adrenaline'));
        pauseButton.addEventListener('click', togglePause);
        // Mouse fallback (kept same)
        shootBtn.addEventListener('mousedown', (e) => handleTouchStart(e, 'shoot')); shootBtn.addEventListener('mouseup', (e) => handleTouchEnd(e, 'shoot')); shootBtn.addEventListener('mouseleave', (e) => handleTouchEnd(e, 'shoot'));
        grenadeBtn.addEventListener('mousedown', (e) => handleTouchStart(e, 'grenade')); grenadeBtn.addEventListener('mouseup', (e) => handleTouchEnd(e, 'grenade')); grenadeBtn.addEventListener('mouseleave', (e) => handleTouchEnd(e, 'grenade'));
        rocketBtn.addEventListener('mousedown', (e) => handleTouchStart(e, 'rocket')); rocketBtn.addEventListener('mouseup', (e) => handleTouchEnd(e, 'rocket')); rocketBtn.addEventListener('mouseleave', (e) => handleTouchEnd(e, 'rocket'));
        repairBtn.addEventListener('mousedown', (e) => handleTouchStart(e, 'repair')); repairBtn.addEventListener('mouseup', (e) => handleTouchEnd(e, 'repair')); repairBtn.addEventListener('mouseleave', (e) => handleTouchEnd(e, 'repair'));
        airstrikeBtn.addEventListener('mousedown', (e) => handleTouchStart(e, 'airstrike')); airstrikeBtn.addEventListener('mouseup', (e) => handleTouchEnd(e, 'airstrike')); airstrikeBtn.addEventListener('mouseleave', (e) => handleTouchEnd(e, 'airstrike'));
        adrenalineBtn.addEventListener('mousedown', (e) => handleTouchStart(e, 'adrenaline')); adrenalineBtn.addEventListener('mouseup', (e) => handleTouchEnd(e, 'adrenaline')); adrenalineBtn.addEventListener('mouseleave', (e) => handleTouchEnd(e, 'adrenaline'));


        function getMousePos(canvas, evt) { const rect = canvas.getBoundingClientRect(); return { x: evt.clientX - rect.left, y: evt.clientY - rect.top }; }
        canvas.addEventListener('mousemove', (evt) => { if (isDeploymentPhase) { mousePos = getMousePos(canvas, evt); } });
        canvas.addEventListener('click', (evt) => { if (isDeploymentPhase && deploymentsAvailable > 0) { placeBarbedWire(); } });
        canvas.addEventListener('touchstart', (evt) => { if (isDeploymentPhase && deploymentsAvailable > 0) { mousePos = getMousePos(canvas, evt.touches[0]); placeBarbedWire(); evt.preventDefault();} }, { passive: false });


        // --- Utility Functions ---
        function drawRect(x, y, width, height, color) { ctx.fillStyle = color; ctx.fillRect(x, y, width, height); }
        function drawLine(x1, y1, x2, y2, color, lineWidth) { ctx.strokeStyle = color; ctx.lineWidth = lineWidth; ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke(); }
        function drawCircle(x, y, radius, color) { ctx.fillStyle = color; ctx.beginPath(); ctx.arc(x, y, radius, 0, Math.PI * 2); ctx.fill(); }
        function drawRoundRect(x, y, width, height, radius, color) { /* ... (same) ... */ ctx.fillStyle = color; ctx.beginPath(); ctx.moveTo(x + radius, y); ctx.lineTo(x + width - radius, y); ctx.quadraticCurveTo(x + width, y, x + width, y + radius); ctx.lineTo(x + width, y + height - radius); ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height); ctx.lineTo(x + radius, y + height); ctx.quadraticCurveTo(x, y + height, x, y + height - radius); ctx.lineTo(x, y + radius); ctx.quadraticCurveTo(x, y, x + radius, y); ctx.closePath(); ctx.fill(); }


        function clearCanvas() { // Reverted to simple gradient, removed parallax
            const skyGradient = ctx.createLinearGradient(0, 0, 0, canvas.height); // Gradient for whole canvas
            skyGradient.addColorStop(0, '#696969'); skyGradient.addColorStop(0.6, '#8B8378'); // Adjust stops
            skyGradient.addColorStop(1, '#A08B70');
            ctx.fillStyle = skyGradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height); // Fill entire canvas

            // Draw ground area separately
            const groundY = backTrenchY + playerHeight; // Where the visible ground starts
            ctx.fillStyle = '#6B4423'; // Ground color
            ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);

            // Add ground texture (specks)
            for (let i = 0; i < 150; i++) { // More specks?
                const speckX = Math.random() * canvas.width;
                const speckY = groundY + Math.random() * (canvas.height - groundY);
                const speckSize = Math.random() * 1.5 + 0.5;
                const speckColor = Math.random() < 0.5 ? 'rgba(75, 58, 42, 0.7)' : 'rgba(160, 131, 100, 0.5)';
                drawRect(speckX, speckY, speckSize, speckSize, speckColor);
            }
        }

        // --- Collision Detection ---
         function checkAABBCollision(rect1, rect2) { return (rect1.x < rect2.x + rect2.width && rect1.x + rect1.width > rect2.x && rect1.y < rect2.y + rect2.height && rect1.y + rect1.height > rect2.y); }
        function checkPlayerEnemyCollision(playerRect, enemyRect) { const pL = playerRect.x - playerRect.width / 2; const pR = playerRect.x + playerRect.width / 2; return (pL < enemyRect.x + enemyRect.width && pR > enemyRect.x && playerRect.y < enemyRect.y + enemyRect.height && playerRect.y + playerRect.height > enemyRect.y); }
        function checkBulletEnemyCollision(bullet, enemy) { return checkAABBCollision(bullet, enemy); }
        function checkEnemyObstacleCollision(enemy, obstacle) { return checkAABBCollision(enemy, obstacle); }
        function checkCircleRectCollision(circle, rect) { const distX = Math.abs(circle.x - rect.x - rect.width / 2); const distY = Math.abs(circle.y - rect.y - rect.height / 2); if (distX > (rect.width / 2 + circle.radius)) { return false; } if (distY > (rect.height / 2 + circle.radius)) { return false; } if (distX <= (rect.width / 2)) { return true; } if (distY <= (rect.height / 2)) { return true; } const dx = distX - rect.width / 2; const dy = distY - rect.height / 2; return (dx * dx + dy * dy <= (circle.radius * circle.radius)); }
        function checkEnemyBulletTargetCollision(bullet, target) { const targetX = target.x - target.width / 2; const targetRect = { x: targetX, y: target.y, width: target.width, height: target.height }; return checkAABBCollision(bullet, targetRect); }


        // --- Particle & Effects Systems ---
        function createBloodEffect(x, y) { /* ... (same) ... */ const particleCount = 7 + Math.floor(Math.random() * 6); for (let i = 0; i < particleCount; i++) { particles.push({ x: x, y: y, dx: (Math.random() - 0.5) * 2.5, dy: (Math.random() - 0.5) * 3.5 - 1.5, life: particleLife + Math.random() * 15, color: bloodParticleColor, size: Math.random() * 2.5 + 1 }); } }
        function createImpactEffect(x, y) { // Dust/debris on impact
            const particleCount = 3 + Math.floor(Math.random() * 3);
            for (let i = 0; i < particleCount; i++) {
                particles.push({ x: x, y: y, dx: (Math.random() - 0.5) * 1.5, dy: (Math.random() - 0.5) * 1.5 - 0.5, life: particleLife * 0.5 + Math.random() * 10, color: debrisParticleColor, size: Math.random() * 1.5 + 1, type: 'debris' });
            }
        }
        function createSparkEffect(x, y) { // Sparks for ricochet
             const particleCount = 2 + Math.floor(Math.random() * 2);
             for (let i = 0; i < particleCount; i++) { particles.push({ x: x, y: y, dx: (Math.random() - 0.5) * 3, dy: (Math.random() - 0.5) * 3 - 1, life: particleLife * 0.3 + Math.random() * 5, color: sparkParticleColor, size: Math.random() * 1 + 1, type: 'spark' }); }
        }
        function createHitMarker(x, y) { hitMarkers.push({ x: x, y: y, life: hitMarkerLife }); }

        function updateParticles() { /* ... (same) ... */ for (let i = particles.length - 1; i >= 0; i--) { const p = particles[i]; p.x += p.dx; p.y += p.dy; p.dy += particleGravity; p.life--; if (p.life <= 0) { particles.splice(i, 1); } } }
        function createMuzzleFlash(x, y) { /* ... (same) ... */ muzzleFlashes.push({ x: x, y: y, life: muzzleFlashLife, size: 8 + Math.random() * 4 }); }
        function updateMuzzleFlashes() { /* ... (same) ... */ for (let i = muzzleFlashes.length - 1; i >= 0; i--) { muzzleFlashes[i].life--; if (muzzleFlashes[i].life <= 0) { muzzleFlashes.splice(i, 1); } } }
        function createExplosion(x, y, radius, isRocket = false) { // Added debris to explosion
             const magnitude = isRocket ? baseScreenShakeMagnitude * 1.5 : baseScreenShakeMagnitude; const duration = isRocket ? baseScreenShakeDuration * 1.5 : baseScreenShakeDuration;
             explosions.push({ x: x, y: y, radius: radius, life: explosionLife, maxLife: explosionLife, color: isRocket ? 'rgba(255, 165, 0, 0.8)' : explosionColor });
             triggerScreenShake(magnitude, duration);
             if (toneStarted) { explosionSound.triggerAttackRelease(isRocket ? "A1" : "C2", "0.6", getNextSoundTime()); }
             const debrisCount = 5 + Math.floor(Math.random() * 5);
             for (let i = 0; i < debrisCount; i++) { particles.push({ x: x, y: y, dx: (Math.random() - 0.5) * 4, dy: (Math.random() - 0.5) * 4 - 1, life: particleLife * 1.5 + Math.random() * 15, color: debrisParticleColor, size: Math.random() * 2 + 1, type: 'debris' }); }
        }
        function updateExplosions() { /* ... (same) ... */ for (let i = explosions.length - 1; i >= 0; i--) { explosions[i].life--; if (explosions[i].life <= 0) { explosions.splice(i, 1); } } }
        function triggerScreenShake(magnitude, duration) { /* ... (same) ... */ screenShakeMagnitude = magnitude; screenShakeDuration = duration; }
        function updateScreenShake() { /* ... (same) ... */ if (screenShakeDuration > 0) { screenShakeDuration--; if (screenShakeDuration === 0) { screenShakeMagnitude = 0; } } }
        function createHealEffect(x, y) { /* ... (same) ... */ const particleCount = 4 + Math.floor(Math.random() * 4); for (let i = 0; i < particleCount; i++) { particles.push({ x: x, y: y, dx: (Math.random() - 0.5) * 1, dy: -Math.random() * 1 - 0.5, life: particleLife * 0.8 + Math.random() * 10, color: 'rgba(0, 255, 0, 0.6)', size: Math.random() * 2 + 1 }); } }
        function createBuffEffect(x, y) { /* ... (same) ... */ const particleCount = 3 + Math.floor(Math.random() * 3); for (let i = 0; i < particleCount; i++) { particles.push({ x: x, y: y, dx: (Math.random() - 0.5) * 0.5, dy: -Math.random() * 0.5 - 0.2, life: particleLife * 0.5, color: 'rgba(255, 255, 0, 0.5)', size: Math.random() + 1 }); } }
        function updateHitMarkers() { for (let i = hitMarkers.length - 1; i >= 0; i--) { hitMarkers[i].life--; if (hitMarkers[i].life <= 0) { hitMarkers.splice(i, 1); } } }
        function updateAirstrike() {
             if (!airstrikeActive) return;
             airstrikeTimer--;
             // Drop bombs periodically during the airstrike
             if (airstrikeTimer > 0 && airstrikeTimer % Math.floor(airstrikeDuration / airstrikesPerCall) === 0) {
                 const dropX = Math.random() * canvas.width;
                 const dropY = -20; // Start above screen
                 mortarShells.push({
                     x: dropX, y: dropY, dx: 0, dy: 4, // Falling straight down faster
                     targetY: canvas.height * (0.1 + Math.random() * 0.7), // Target random spot on battlefield
                     radius: 5, color: '#111' // Bomb color
                 });
                 if (toneStarted) { mortarLaunchSound.triggerAttackRelease("C2", "0.3", getNextSoundTime()); } // Whistle sound?
             }
             if (airstrikeTimer <= 0) {
                 airstrikeActive = false;
             }
        }
        function updateAdrenaline() {
             if (!adrenalineActive) return;
             adrenalineTimer--;
             if (adrenalineTimer <= 0) {
                 adrenalineActive = false;
                 adrenalineOverlay.style.display = 'none';
             }
        }

        // --- Ability Activation ---
        function activateTrenchRepair() {
             if (trenchRepairAbilityCooldownCounter <= 0 && trenchHealth < maxTrenchHealth) {
                 trenchHealth = Math.min(maxTrenchHealth, trenchHealth + trenchRepairAbilityAmount);
                 trenchRepairAbilityCooldownCounter = trenchRepairAbilityCooldownTime;
                 if (toneStarted) { repairSound.triggerAttackRelease("C4", "0.2", getNextSoundTime()); }
                 updateUI();
             }
        }
        function activateAirstrike() {
             if (airstrikeAbilityCooldownCounter <= 0) {
                 airstrikeActive = true;
                 airstrikeTimer = airstrikeDuration;
                 airstrikeAbilityCooldownCounter = airstrikeAbilityCooldownTime;
                 if (toneStarted) { airstrikeWarnSound.triggerAttackRelease("F5", "0.5", getNextSoundTime()); }
                 updateUI();
             }
        }
        function activateAdrenaline() {
             if (adrenalineAbilityCooldownCounter <= 0) {
                 adrenalineActive = true;
                 adrenalineTimer = adrenalineDuration;
                 adrenalineAbilityCooldownCounter = adrenalineAbilityCooldownTime;
                 adrenalineOverlay.style.display = 'block';
                 if (toneStarted) { adrenalineSound.triggerAttackRelease("A3", "0.4", getNextSoundTime()); }
                 updateUI();
             }
        }


        // --- Game Logic Functions ---
        function updatePlayer() { // Added ability cooldown updates & passive trench repair
             player.dx = 0; if (keys.ArrowLeft || touchLeft) player.dx = -currentPlayerSpeed; if (keys.ArrowRight || touchRight) player.dx = currentPlayerSpeed; player.x += player.dx; const halfWidth = player.width / 2; player.x = Math.max(halfWidth, Math.min(canvas.width - halfWidth, player.x));
             let isBuffedByOfficer = false; friendlyNPCs.forEach(npc => { if (npc.isOfficer) { const distSq = (player.x - npc.x)**2 + (player.y - npc.y)**2; if (distSq < officerBuffRadius**2) isBuffedByOfficer = true; } }); const officerBuffMultiplier = isBuffedByOfficer ? officerFireRateBuff : 1;
             if (playerPowerUp.timer > 0) { playerPowerUp.timer--; if(playerPowerUp.type === 'rapidFire') currentShootCooldownTime = rapidFireCooldown * officerBuffMultiplier; else if(playerPowerUp.type === 'shotgun') currentShootCooldownTime = baseShootCooldownTime * 1.5 * officerBuffMultiplier; else currentShootCooldownTime = baseShootCooldownTime * officerBuffMultiplier; if (playerPowerUp.timer <= 0) { playerPowerUp.type = null; currentShootCooldownTime = baseShootCooldownTime * officerBuffMultiplier; powerupTimerElement.style.display = 'none'; } else { powerupTimeLeftElement.textContent = Math.ceil(playerPowerUp.timer / 60); } } else { currentShootCooldownTime = baseShootCooldownTime * officerBuffMultiplier; }
             if (shootCooldownCounter > 0) shootCooldownCounter--; if ((keys.Space || touchShoot) && shootCooldownCounter <= 0) { shootBullet(); shootCooldownCounter = currentShootCooldownTime; }
             if (grenadeCooldownCounter > 0) grenadeCooldownCounter--;
             if (rocketCooldownCounter > 0) rocketCooldownCounter--;
             if (trenchRepairAbilityCooldownCounter > 0) trenchRepairAbilityCooldownCounter--;
             if (airstrikeAbilityCooldownCounter > 0) airstrikeAbilityCooldownCounter--;
             if (adrenalineAbilityCooldownCounter > 0) adrenalineAbilityCooldownCounter--;
             // Passive Trench Repair
             if (trenchHealth < maxTrenchHealth && trenchHealth > 0) { trenchHealth = Math.min(maxTrenchHealth, trenchHealth + trenchRepairRate * upgradeLevels.trenchRepair); updateUI(); }
             // Trench switch cooldown update (even if not used for movement)
             if (playerTrenchSwitchCooldown > 0) playerTrenchSwitchCooldown--;
        }

        // Removed switchTrench function

        function shootBullet() {
            createMuzzleFlash(player.x, player.y - player.gunLength);
            const damageToApply = adrenalineActive ? currentBulletDamage * 1.5 : currentBulletDamage;
            if (playerPowerUp.type === 'shotgun') {
                if (toneStarted) { shotgunSound.triggerAttackRelease("8n", getNextSoundTime()); }
                for (let i = 0; i < shotgunPellets; i++) { const angleOffset = (Math.random() - 0.5) * shotgunSpread; const speedX = Math.sin(angleOffset) * bulletSpeed * 0.5; const speedY = Math.cos(angleOffset) * bulletSpeed; bullets.push({ x: player.x - bulletWidth / 2, y: player.y - player.gunLength, width: bulletWidth, height: bulletHeight, color: '#FFD700', speed: speedY, dx: speedX, damage: damageToApply * 0.6 }); }
            } else { if (toneStarted) { shootSound.triggerAttackRelease("16n", getNextSoundTime()); } bullets.push({ x: player.x - bulletWidth / 2, y: player.y - player.gunLength, width: bulletWidth, height: bulletHeight, color: '#FFFF99', speed: bulletSpeed, dx: 0, damage: damageToApply }); }
        }
        function shootRocket() {
             if (rocketCount <= 0 || rocketCooldownCounter > 0) return;
             rocketCount--; rocketCooldownCounter = rocketCooldownTime; updateUI();
             if (toneStarted) { rocketLaunchSound.triggerAttackRelease("C3", "0.5", getNextSoundTime()); }
             createMuzzleFlash(player.x, player.y - player.gunLength);
             rockets.push({ x: player.x - rocketWidth / 2, y: player.y - player.gunLength, width: rocketWidth, height: rocketHeight, color: '#FFA500', speed: rocketSpeed, fuse: rocketFuseTime }); // Add fuse
        }
        function throwGrenade() { // Straight trajectory
             if (grenadeCount <= 0 || grenadeCooldownCounter > 0) return;
             grenadeCount--; grenadeCooldownCounter = grenadeCooldownTime; updateUI();
             grenades.push({ x: player.x, y: player.y - player.gunLength, // Start from gun tip
                             dx: 0, dy: -grenadeThrowSpeed, // Straight up
                             fuse: grenadeFuseTime, radius: 5, color: '#333' });
        }
        function updateGrenades() { // Straight trajectory logic
            for (let i = grenades.length - 1; i >= 0; i--) {
                const g = grenades[i];
                g.y += g.dy; // Move straight up
                g.fuse--;
                if (g.fuse <= 0 || g.y < 0) {
                    createExplosion(g.x, g.y < 0 ? 0 : g.y, grenadeRadius);
                    for(let j = enemies.length - 1; j >= 0; j--) { const enemy = enemies[j]; if (checkCircleRectCollision({ x: g.x, y: g.y < 0 ? 0 : g.y, radius: grenadeRadius }, enemy)) { enemy.health -= currentGrenadeDamage; if (enemy.health <= 0) { score += 15; createBloodEffect(enemy.x + enemy.width / 2, enemy.y + enemy.height / 2); if (Math.random() < powerUpDropChance) { spawnPowerUp(enemy.x + enemy.width / 2, enemy.y + enemy.height / 2); } if (toneStarted) { enemyDeathSound.start(getNextSoundTime()); } enemies.splice(j, 1); enemiesKilledThisWave++; } } };
                    grenades.splice(i, 1); updateUI();
                }
            }
        }
        function updateRockets() { // Added fuse logic
             for (let i = rockets.length - 1; i >= 0; i--) {
                 const r = rockets[i]; r.y -= r.speed; r.fuse--;
                 let hitEnemy = false;
                 for (let j = enemies.length - 1; j >= 0; j--) { if (checkAABBCollision(r, enemies[j])) { hitEnemy = true; break; } }
                 if (hitEnemy || r.fuse <= 0 || r.y + r.height < 0) {
                     const explosionY = r.y < 0 ? 0 : r.y; createExplosion(r.x + r.width / 2, explosionY, rocketRadius, true);
                     for(let k = enemies.length - 1; k >= 0; k--) { const enemy = enemies[k]; if (checkCircleRectCollision({ x: r.x + r.width / 2, y: explosionY, radius: rocketRadius }, enemy)) { enemy.health -= currentRocketDamage; if (enemy.health <= 0) { score += 25; createBloodEffect(enemy.x + enemy.width / 2, enemy.y + enemy.height / 2); if (Math.random() < powerUpDropChance * 1.5) { spawnPowerUp(enemy.x + enemy.width / 2, enemy.y + enemy.height / 2); } if (toneStarted) { enemyDeathSound.start(getNextSoundTime()); } enemies.splice(k, 1); enemiesKilledThisWave++; } } };
                     rockets.splice(i, 1); updateUI();
                 }
             }
        }

        function updateBullets() { // Updated to handle dx for shotgun & impacts
             for (let i = bullets.length - 1; i >= 0; i--) {
                 const bullet = bullets[i];
                 bullet.y -= bullet.speed;
                 bullet.x += bullet.dx; // Apply horizontal speed

                 // Remove if off-screen (top or sides)
                 if (bullet.y + bullet.height < 0 || bullet.x < 0 || bullet.x + bullet.width > canvas.width) {
                     bullets.splice(i, 1);
                 }
             }
        }
        function updateNPCBullets() { /* ... (same) ... */ for (let i = npcBullets.length - 1; i >= 0; i--) { npcBullets[i].y -= npcBullets[i].speed; if (npcBullets[i].y + npcBullets[i].height < 0) npcBullets.splice(i, 1); } }
        function updateEnemyBullets() { /* ... (same) ... */ for (let i = enemyBullets.length - 1; i >= 0; i--) { const bullet = enemyBullets[i]; bullet.y += bullet.speed * (adrenalineActive ? adrenalineSlowFactor : 1); if (bullet.y > canvas.height) { enemyBullets.splice(i, 1); } } } // Slowed by adrenaline
        function updateMortarShells() { // Slowed by adrenaline
             for (let i = mortarShells.length - 1; i >= 0; i--) {
                 const shell = mortarShells[i];
                 const speedMultiplier = adrenalineActive ? adrenalineSlowFactor : 1;
                 shell.x += shell.dx * speedMultiplier;
                 shell.y += shell.dy * speedMultiplier;
                 shell.dy += particleGravity * 0.5; // Keep gravity constant

                 if (shell.y >= shell.targetY) {
                     createExplosion(shell.x, shell.targetY, mortarRadius);
                     const explosionCircle = { x: shell.x, y: shell.targetY, radius: mortarRadius };
                     if (checkCircleRectCollision(explosionCircle, { x: player.x - player.width / 2, y: player.y, width: player.width, height: player.height })) { playerHealth -= mortarDamage; updateUI(); if (playerHealth <= 0) { triggerGameOver(); return; } }
                     friendlyNPCs.forEach(npc => { if (checkCircleRectCollision(explosionCircle, { x: npc.x - npc.width / 2, y: npc.y, width: npc.width, height: npc.height })) { npc.health -= mortarDamage; npc.isHit = true; npc.hitTimer = npcHitFlashDuration;} }); // Damage NPC and trigger flash
                     mortarShells.splice(i, 1);
                 }
             }
        }

        function updateNPCs() { // Added movement, targeting, buff check, hit timer
            let officerPresent = false;
            let officerX = 0, officerY = 0;
            friendlyNPCs.forEach(npc => { if (npc.isOfficer) { officerPresent = true; officerX = npc.x; officerY = npc.y; } });

            for (let i = friendlyNPCs.length - 1; i >= 0; i--) {
                const npc = friendlyNPCs[i];
                // Update hit flash timer
                if (npc.hitTimer > 0) npc.hitTimer--;
                if (npc.hitTimer <= 0) npc.isHit = false;

                if (npc.health <= 0) { createBloodEffect(npc.x, npc.y + npc.height / 2); friendlyNPCs.splice(i, 1); updateUI(); continue; }

                // Movement Logic
                npc.moveCooldown--;
                if (npc.moveCooldown <= 0) {
                    npc.targetX = npc.initialX + (Math.random() - 0.5) * npcMoveRange * 2;
                    npc.targetX = Math.max(npc.width/2, Math.min(canvas.width - npc.width/2, npc.targetX));
                    npc.moveCooldown = npcMoveCooldown + Math.random() * 60;
                }
                if (Math.abs(npc.x - npc.targetX) > playerSpeed * 0.2) { npc.x += Math.sign(npc.targetX - npc.x) * playerSpeed * 0.1; }

                // Check for officer buff
                let isBuffedByOfficer = false;
                if(officerPresent && !npc.isOfficer) { // Officer doesn't buff self
                     const distSq = (npc.x - officerX)**2 + (npc.y - officerY)**2;
                     if (distSq < officerBuffRadius**2) isBuffedByOfficer = true;
                }
                const currentNpcShootCooldown = (npcShootCooldownBase + Math.random() * npcShootCooldownVariance) * (isBuffedByOfficer ? officerFireRateBuff : 1);


                // Shooting Logic (Targeting Priority)
                npc.shootCooldown--;
                if (npc.shootCooldown <= 0 && enemies.length > 0) {
                    let target = null;
                    let minDangerDistSq = Infinity;
                    let minClosestDistSq = Infinity;
                    let closestEnemy = null;

                    // Find closest dangerous enemy (Shooter/Mortar/Commander) within range first
                    enemies.forEach(enemy => {
                         if (['shooter', 'mortar', 'commander'].includes(enemy.type)) { // Prioritize dangerous types
                             const distSq = (enemy.x - npc.x)**2 + (enemy.y - npc.y)**2;
                             if (distSq < minDangerDistSq) {
                                 minDangerDistSq = distSq;
                                 target = enemy;
                             }
                         }
                         // Also track the overall closest enemy
                         const distToTrenchSq = (enemy.x - npc.x)**2 + (enemy.y - backTrenchY)**2 * 2; // Compare to back trench Y
                         if (distToTrenchSq < minClosestDistSq) {
                              minClosestDistSq = distToTrenchSq;
                              closestEnemy = enemy;
                         }
                    });

                    // If no dangerous enemy found nearby, target the overall closest
                    if (!target) {
                         target = closestEnemy;
                    }


                    if (target) { // Check if a target was actually found
                        if (toneStarted) { npcShootSound.triggerAttackRelease("16n", getNextSoundTime()); }
                        createMuzzleFlash(npc.x, npc.y - npc.gunLength);
                        npcBullets.push({ x: npc.x - npc.gunWidth / 2, y: npc.y - npc.gunLength, width: bulletWidth, height: bulletHeight, color: '#ADD8E6', speed: bulletSpeed * 0.8, dx: 0 });
                        npc.shootCooldown = currentNpcShootCooldown; // Use potentially buffed cooldown
                    } else {
                        npc.shootCooldown = 30; // No target, check again soon
                    }
                }
            }
        }
        function updateAmbientNPCs() {
             ambientNPCs.forEach(npc => {
                 if (Math.abs(npc.x - npc.targetX) < npc.speed) { npc.targetX = Math.random() * (canvas.width - npc.width * 2) + npc.width; }
                 else { npc.x += Math.sign(npc.targetX - npc.x) * npc.speed; }
                 npc.animOffset = Math.sin(Date.now() / 200 + npc.animPhase) * 2;
                 npc.legAnimTimer = (npc.legAnimTimer + 1) % enemyAnimSpeed;
             });
        }

        function spawnEnemy() { // Added shield, medic, commander types
             if (enemiesSpawnedThisWave >= enemiesToSpawnThisWave) return;
             const x = Math.random()*(canvas.width-enemyWidth); const y = 0-enemyHeight;
             let type = 'standard'; let health = 20; let speed = baseEnemySpeed + (Math.random() * 0.5 - 0.25); let bodyColor = enemyBodyColor; let shootCooldown = -1; let mortarCooldown = -1; let healCooldown = -1; let buffCooldown = -1; let dx = 0;
             let imgKey = 'enemyStandard';

             const rand = Math.random();
              if (currentWave >= 8 && rand < 0.08) { type = 'commander'; health = 60; speed *= 0.5; bodyColor = commanderColor; buffCooldown = 120 + Math.random() * 60; imgKey = 'enemyCommander';}
              else if (currentWave >= 6 && rand < 0.18) { type = 'medic'; health = 30; speed *= 0.7; bodyColor = medicColor; healCooldown = medicHealCooldown + Math.random() * 60; imgKey = 'enemyMedic';}
              else if (currentWave >= 7 && rand < 0.28) { type = 'shield'; health = 80; speed *= 0.3; bodyColor = shieldEnemyColor; imgKey = 'enemyShield';}
              else if (currentWave >= 6 && rand < 0.4) { type = 'mortar'; health = 40; speed *= 0.4; bodyColor = mortarEnemyColor; mortarCooldown = 180 + Math.random() * 120; imgKey = 'enemyMortar';}
             else if (currentWave >= 5 && rand < 0.55) { type = 'shooter'; health = 30; speed *= 0.6; bodyColor = shooterEnemyColor; shootCooldown = 90 + Math.random() * 60; imgKey = 'enemyShooter';}
             else if (currentWave >= 4 && rand < 0.7) { type = 'fast'; health = 15; speed *= 1.8; bodyColor = fastEnemyColor; imgKey = 'enemyFast';}
             else if (currentWave >= 2 && rand < 0.85) { type = 'tough'; health = 50; speed *= 0.8; bodyColor = toughEnemyColor; imgKey = 'enemyTough';}

             // Add chance for diagonal movement
             if (['standard', 'fast', 'tough', 'shield', 'medic', 'commander'].includes(type)) {
                 if (Math.random() < 0.2) {
                     const startCorner = Math.random() < 0.5 ? 'left' : 'right';
                     const spawnX = startCorner === 'left' ? -enemyWidth : canvas.width;
                     const targetXCenter = canvas.width * (0.3 + Math.random() * 0.4);
                     dx = (targetXCenter - spawnX) / (canvas.height / speed) * 0.5;
                     enemies.push({ x:spawnX, y:y, width:enemyWidth, height:enemyHeight, type: type, health: health, maxHealth: health, bodyColor: bodyColor, headColor: enemyHeadColor, baseSpeed:speed, currentSpeed:speed, dx: dx, state: 'advancing', shootCooldown: shootCooldown, mortarCooldown: mortarCooldown, healCooldown: healCooldown, buffCooldown: buffCooldown, buffTimer: 0, stopY: canvas.height * (type === 'mortar' ? 0.15 : (type === 'shooter' ? 0.3 : (type === 'medic' || type === 'commander' ? 0.4 : 1.0)) + Math.random() * 0.3), legAnimFrame: 0, legAnimTimer: 0, imgKey: imgKey });
                     enemiesSpawnedThisWave++;
                     return;
                 }
             }

             // Default spawn
             enemies.push({ x:x, y:y, width:enemyWidth, height:enemyHeight, type: type, health: health, maxHealth: health, bodyColor: bodyColor, headColor: enemyHeadColor, baseSpeed:speed, currentSpeed:speed, dx: dx, state: 'advancing', shootCooldown: shootCooldown, mortarCooldown: mortarCooldown, healCooldown: healCooldown, buffCooldown: buffCooldown, buffTimer: 0, stopY: canvas.height * (type === 'mortar' ? 0.15 : (type === 'shooter' ? 0.3 : (type === 'medic' || type === 'commander' ? 0.4 : 1.0)) + Math.random() * 0.3), legAnimFrame: 0, legAnimTimer: 0, imgKey: imgKey });
             enemiesSpawnedThisWave++;
        }
        function updateEnemies() { // Includes new AI logic
            // Reset buffs before commander applies them
            enemies.forEach(e => { if(e.buffTimer > 0) e.buffTimer--; else e.isBuffed = false; });

            for (let i = enemies.length - 1; i >= 0; i--) {
                const enemy = enemies[i]; let isOnObstacle = false; for (const obs of obstacles) { if (checkEnemyObstacleCollision(enemy, obs)) { isOnObstacle = true; break; } }
                // Apply commander buff if active
                const currentSpeedFactor = enemy.isBuffed ? commanderSpeedBuff : 1;
                // Apply adrenaline slow factor
                const adrenalineMultiplier = adrenalineActive ? adrenalineSlowFactor : 1;
                enemy.currentSpeed = (isOnObstacle ? enemy.baseSpeed * obstacleSlowFactor : enemy.baseSpeed * currentSpeedFactor) * adrenalineMultiplier;


                // Update leg animation timer
                if(enemy.state === 'advancing') {
                     enemy.legAnimTimer = (enemy.legAnimTimer + 1);
                     // Adjust animation speed based on current speed relative to base speed
                     const animSpeedDivisor = Math.max(0.1, enemy.currentSpeed / enemy.baseSpeed); // Avoid division by zero
                     if (enemy.legAnimTimer >= enemyAnimSpeed / animSpeedDivisor) {
                         enemy.legAnimFrame = 1 - enemy.legAnimFrame;
                         enemy.legAnimTimer = 0;
                     }
                } else { enemy.legAnimFrame = 0; }

                // --- Enemy State Machine ---
                if (enemy.state === 'advancing') {
                    enemy.y += enemy.currentSpeed; enemy.x += enemy.dx * enemy.currentSpeed / enemy.baseSpeed; // Use base speed for dx scaling
                    // Boundary check for horizontal movement - Keep within canvas
                    if (enemy.dx > 0 && enemy.x + enemy.width > canvas.width) { enemy.x = canvas.width - enemy.width; enemy.dx = 0; }
                    else if (enemy.dx < 0 && enemy.x < 0) { enemy.x = 0; enemy.dx = 0; }

                    // Shooter cover logic
                    if (enemy.type === 'shooter' && enemy.dx === 0) {
                         for (const obs of obstacles) { if (obs.y > enemy.y + enemy.height && obs.y < enemy.y + enemy.height * 5 && Math.abs((obs.x + obs.width/2) - (enemy.x + enemy.width/2)) < obs.width) { enemy.state = 'taking_cover'; enemy.coverTarget = obs; break; } }
                    }

                    if (enemy.y >= enemy.stopY) {
                        if (enemy.type === 'shooter') enemy.state = 'shooting';
                        else if (enemy.type === 'mortar') enemy.state = 'firing_mortar';
                        else if (enemy.type === 'medic') enemy.state = 'healing';
                        else if (enemy.type === 'commander') enemy.state = 'buffing';
                    }
                } else if (enemy.state === 'taking_cover') {
                    const targetCoverX = enemy.coverTarget.x + enemy.coverTarget.width / 2;
                    if (Math.abs(enemy.x + enemy.width/2 - targetCoverX) > enemy.currentSpeed) { enemy.x += Math.sign(targetCoverX - (enemy.x + enemy.width/2)) * enemy.currentSpeed * 0.5; }
                    enemy.y += enemy.currentSpeed * 0.3; // Still move down slowly while taking cover
                    if (enemy.y > enemy.coverTarget.y && Math.abs(enemy.x + enemy.width/2 - targetCoverX) <= enemy.currentSpeed) { enemy.state = 'in_cover'; enemy.shootCooldown = 30; }
                } else if (enemy.state === 'in_cover') { enemy.state = 'shooting'; }

                // Action States (Apply adrenaline slow factor to cooldowns?) - Maybe not, just visual slow
                if (enemy.state === 'shooting') { enemy.shootCooldown--; if (enemy.shootCooldown <= 0) { if (toneStarted) { enemyShootSound.triggerAttackRelease("16n", getNextSoundTime()); } createMuzzleFlash(enemy.x + enemy.width / 2, enemy.y + enemy.height * 0.5); enemyBullets.push({ x: enemy.x + enemy.width / 2 - bulletWidth / 2, y: enemy.y + enemy.height * 0.5, width: bulletWidth, height: bulletHeight, color: '#FF6347', speed: bulletSpeed * 0.6 }); enemy.shootCooldown = 100 + Math.random() * 50; } }
                else if (enemy.state === 'firing_mortar') { enemy.mortarCooldown--; if (enemy.mortarCooldown <= 0) { if (toneStarted) { mortarLaunchSound.triggerAttackRelease("G3", "0.5", getNextSoundTime()); }
                    let targetX = player.x; if(friendlyNPCs.length > 0 && Math.random() < 0.6) { targetX = friendlyNPCs[Math.floor(Math.random() * friendlyNPCs.length)].x; } targetX += (Math.random() - 0.5) * (canvas.width * 0.3);
                    const targetY = canvas.height - trenchHeight + (Math.random() * trenchHeight * 0.8); const dx = (targetX - enemy.x) / 100; const dy = -mortarShellSpeed; mortarShells.push({ x: enemy.x + enemy.width / 2, y: enemy.y + enemy.height / 2, dx: dx, dy: dy, targetY: targetY, radius: 4, color: '#444' }); enemy.mortarCooldown = 240 + Math.random() * 120; } }
                else if (enemy.state === 'healing') {
                    enemy.healCooldown--;
                    if (enemy.healCooldown <= 0) {
                        let healed = false;
                        enemies.forEach(otherEnemy => { if (enemy !== otherEnemy && otherEnemy.health < otherEnemy.maxHealth && otherEnemy.type !== 'tank') { const distSq = (enemy.x - otherEnemy.x)**2 + (enemy.y - otherEnemy.y)**2; if (distSq < medicHealRadius**2) { otherEnemy.health = Math.min(otherEnemy.maxHealth, otherEnemy.health + medicHealAmount); createHealEffect(otherEnemy.x + otherEnemy.width/2, otherEnemy.y + otherEnemy.height/2); healed = true; } } });
                        if (healed && toneStarted) { medicHealSound.triggerAttackRelease("G4", "0.2", getNextSoundTime()); }
                        enemy.healCooldown = medicHealCooldown + Math.random() * 30;
                    }
                     enemy.y += enemy.currentSpeed * 0.1; // Advance slowly
                } else if (enemy.state === 'buffing') {
                     enemy.buffCooldown--;
                     if (enemy.buffCooldown <= 0) {
                          let buffed = false; createBuffEffect(enemy.x + enemy.width/2, enemy.y + enemy.height/2);
                          enemies.forEach(otherEnemy => { if (enemy !== otherEnemy && ['standard', 'fast', 'tough', 'shooter', 'shield'].includes(otherEnemy.type)) { const distSq = (enemy.x - otherEnemy.x)**2 + (enemy.y - otherEnemy.y)**2; if (distSq < commanderBuffRadius**2) { otherEnemy.isBuffed = true; otherEnemy.buffTimer = 120; buffed = true; } } });
                          if(buffed && toneStarted) { commanderBuffSound.triggerAttackRelease("C4", "0.3", getNextSoundTime()); }
                          enemy.buffCooldown = 180 + Math.random() * 60;
                     }
                     enemy.y += enemy.currentSpeed * 0.1; // Advance slowly
                }
                // --- End State Machine ---

                // Check if reached trench line
                if (enemy.y + enemy.height > canvas.height - trenchHeight) {
                     if (trenchHealth > 0) {
                         trenchHealth -= enemyTrenchDamage; // Damage trench first
                         if (toneStarted) { trenchDamageSound.triggerAttackRelease("8n", getNextSoundTime()); }
                     } else {
                         playerHealth -= enemyCollisionDamage; // Damage player if trench is breached
                     }
                     enemies.splice(i, 1); // Remove enemy regardless
                     updateUI();
                     if (playerHealth <= 0) { playerHealth = 0; updateUI(); triggerGameOver(); return; }
                 }
            }
        }

        function startNextWave() { // Removed boss logic
            currentWave++;
            // isBossWave = false; // No longer needed
            enemiesSpawnedThisWave = 0; enemiesKilledThisWave = 0;
            enemiesToSpawnThisWave = 5 + currentWave * 3;
            currentEnemySpawnRate = Math.max(30, baseEnemySpawnRate - currentWave * 5);
            waveNotificationElement.textContent = `Wave ${currentWave} Starting!`;
            enemySpawnCounter = 0;
            waveNotificationElement.style.display = 'block';
            setTimeout(() => { waveNotificationElement.style.display = 'none'; }, 2000);
            updateUI();
        }

        function updateWaves() { // Removed boss logic
            if (isDeploymentPhase || isUpgradePhase || isSkillTreePhase) return; // Pause during deployment/upgrade/skill tree

            if (waveTransitionCounter > 0) {
                waveTransitionCounter--;
                if (waveTransitionCounter <= 0) {
                    startNextWave();
                     // Award skill point every 5 waves
                    if (currentWave > 0 && currentWave % 5 === 0) {
                        skillPoints++;
                        updateSkillPointDisplay();
                    }
                }
                return;
            }

            const waveCompleteCondition = (enemiesSpawnedThisWave >= enemiesToSpawnThisWave && enemies.length === 0);

            if (waveCompleteCondition) {
                 if (currentWave > 0 && currentWave % 5 === 0) { startDeploymentPhase(); }
                 else { startUpgradePhase(); } // Go to upgrade phase instead of direct transition
                 return;
            }

            enemySpawnCounter++;
            if (enemySpawnCounter >= currentEnemySpawnRate && enemiesSpawnedThisWave < enemiesToSpawnThisWave) {
                spawnEnemy();
                enemySpawnCounter = 0;
            }
        }

        function spawnPowerUp(x, y) { // Includes shotgun
             let type = 'rapidFire';
             const rand = Math.random();
             const effectiveReinforcementChance = friendlyNPCs.length < maxFriendlyNPCs ? reinforcementDropChance : 0;
             const totalDropChance = powerUpDropChance + effectiveReinforcementChance + healthDropChance + shotgunDropChance;

             if (rand < effectiveReinforcementChance / totalDropChance) { type = 'reinforcements'; }
             else if (rand < (effectiveReinforcementChance + healthDropChance) / totalDropChance) { type = 'healthKit'; }
             else if (rand < (effectiveReinforcementChance + healthDropChance + shotgunDropChance) / totalDropChance) { type = 'shotgun'; }


             powerUps.push({
                 x: x, y: y, type: type, radius: 8,
                 color: type === 'reinforcements' ? '#ADD8E6' : (type === 'healthKit' ? '#90EE90' : (type === 'shotgun' ? '#FFA500' : '#f6e05e')),
                 dy: 1, life: 400
             });
        }
        function updatePowerUps() { // Includes shotgun
             for (let i = powerUps.length - 1; i >= 0; i--) {
                 const p = powerUps[i]; p.y += p.dy; p.life--;
                 const playerRect = { x: player.x - player.width / 2, y: player.y, width: player.width, height: player.height };
                 const powerUpRect = { x: p.x - p.radius, y: p.y - p.radius, width: p.radius * 2, height: p.radius * 2 };
                 if (checkAABBCollision(playerRect, powerUpRect)) {
                     if (p.type === 'rapidFire' || p.type === 'shotgun') { playerPowerUp.type = p.type; playerPowerUp.timer = powerUpDuration; powerupTimerElement.style.display = 'inline'; powerupTypeElement.textContent = p.type === 'rapidFire' ? 'Rapid Fire:' : 'Shotgun:'; powerupTypeIconElement.textContent = p.type === 'rapidFire' ? '🔥' : '💥'; if (toneStarted) { powerUpSound.triggerAttackRelease("C5", "0.2", getNextSoundTime()); } }
                     else if (p.type === 'reinforcements') { addReinforcement(); if (toneStarted) { reinforcementSound.triggerAttackRelease("A4", "0.3", getNextSoundTime()); } }
                     else if (p.type === 'healthKit') { playerHealth = Math.min(100, playerHealth + healthPackAmount); updateUI(); if (toneStarted) { healthSound.triggerAttackRelease("E5", "0.2", getNextSoundTime()); } }
                     powerUps.splice(i, 1);
                 } else if (p.life <= 0 || p.y > canvas.height) { powerUps.splice(i, 1); }
             }
        }
        function addReinforcement() { /* ... (same) ... */ if (friendlyNPCs.length < maxFriendlyNPCs) { let potentialX = [canvas.width * 0.25, canvas.width * 0.75, canvas.width * 0.1, canvas.width * 0.9, canvas.width * 0.5]; let placed = false; for(let px of potentialX) { let spotOccupied = false; for(let npc of friendlyNPCs) { if (Math.abs(npc.x - px) < player.width * 2) { spotOccupied = true; break; } } if (Math.abs(player.x - px) < player.width * 2) { spotOccupied = true; } if (!spotOccupied) { initializeSingleNPC(px); placed = true; break; } } if (!placed) { console.log("Could not find space for reinforcement."); } updateUI(); } }


        function handleCollisions() { // Added score for shield/medic/commander enemy & enemy death sound & hit markers
             // Player Bullet - Enemy Collisions
            for (let i=bullets.length-1; i>=0; i--) { for (let j=enemies.length-1; j>=0; j--) { if (bullets[i] && enemies[j] && checkBulletEnemyCollision(bullets[i], enemies[j])) {
                enemies[j].health -= bullets[i].damage || currentBulletDamage; // Use currentBulletDamage as fallback
                createBloodEffect(enemies[j].x + enemies[j].width / 2, enemies[j].y + enemies[j].height / 2);
                createHitMarker(bullets[i].x, bullets[i].y); // Add hit marker
                bullets.splice(i, 1);
                if (enemies[j].health <= 0) {
                    score += (enemies[j].type === 'tough' ? 20 : (enemies[j].type === 'shooter' ? 15 : (enemies[j].type === 'mortar' ? 25 : (enemies[j].type === 'shield' ? 30 : (enemies[j].type === 'medic' ? 12 : (enemies[j].type === 'commander' ? 40 : 10))))));
                    if (Math.random() < powerUpDropChance) { spawnPowerUp(enemies[j].x + enemies[j].width / 2, enemies[j].y + enemies[j].height / 2); }
                    if (toneStarted) { playerKillSound.start(getNextSoundTime()); } // Use specific player kill sound
                    enemies.splice(j, 1); enemiesKilledThisWave++;
                }
                updateUI(); break;
            } } }
             // NPC Bullet - Enemy Collisions
            for (let i=npcBullets.length-1; i>=0; i--) { for (let j=enemies.length-1; j>=0; j--) { if (npcBullets[i] && enemies[j] && checkBulletEnemyCollision(npcBullets[i], enemies[j])) { enemies[j].health -= npcBulletDamage; createBloodEffect(enemies[j].x + enemies[j].width / 2, enemies[j].y + enemies[j].height / 2); npcBullets.splice(i, 1); if (enemies[j].health <= 0) { score += (enemies[j].type === 'tough' ? 10 : (enemies[j].type === 'shooter' ? 8 : (enemies[j].type === 'mortar' ? 12 : (enemies[j].type === 'shield' ? 15 : (enemies[j].type === 'medic' ? 6 : (enemies[j].type === 'commander' ? 20 : 5)))))); if (Math.random() < powerUpDropChance * 0.5) { spawnPowerUp(enemies[j].x + enemies[j].width / 2, enemies[j].y + enemies[j].height / 2); } if (toneStarted) { enemyDeathSound.start(getNextSoundTime()); } enemies.splice(j, 1); enemiesKilledThisWave++; } updateUI(); break; } } }
            // Enemy Bullet - Player/NPC Collisions
            for (let i = enemyBullets.length - 1; i >= 0; i--) { const bullet = enemyBullets[i]; let hit = false; if (checkEnemyBulletTargetCollision(bullet, player)) { playerHealth -= enemyBulletDamage; enemyBullets.splice(i, 1); updateUI(); hit = true; if (playerHealth <= 0) { triggerGameOver(); return; } } if (!hit) { for (let j = friendlyNPCs.length - 1; j >= 0; j--) { if (checkEnemyBulletTargetCollision(bullet, friendlyNPCs[j])) { friendlyNPCs[j].health -= enemyBulletDamage; friendlyNPCs[j].isHit = true; friendlyNPCs[j].hitTimer = npcHitFlashDuration; enemyBullets.splice(i, 1); hit = true; break; } } } if(hit) break; }
             // Rocket collisions handled in updateRockets
             // Mortar shell collisions handled in updateMortarShells
        }
        function updateUI() { // Added cooldown indicators
            scoreElement.textContent = score; healthElement.textContent = playerHealth; trenchHealthElement.textContent = trenchHealth > 0 ? Math.floor(trenchHealth) : 0; // Use Math.floor here
            waveElement.textContent = currentWave > 0 ? currentWave : (isDeploymentPhase ? 1 : 'Deploy'); grenadeElement.textContent = grenadeCount; rocketElement.textContent = rocketCount; alliesElement.textContent = friendlyNPCs.length; maxAlliesElement.textContent = maxFriendlyNPCs;
            // Powerup Timer
            if (playerPowerUp.timer > 0) { powerupTimerElement.style.display = 'inline'; powerupTypeElement.textContent = playerPowerUp.type === 'rapidFire' ? 'Rapid Fire:' : 'Shotgun:'; powerupTypeIconElement.textContent = playerPowerUp.type === 'rapidFire' ? '🔥' : '💥'; powerupTimeLeftElement.textContent = Math.ceil(playerPowerUp.timer / 60); } else { powerupTimerElement.style.display = 'none'; }
            // Cooldown Indicators
            grenadeCooldownBar.style.width = `${Math.min(100, 100 - (grenadeCooldownCounter / grenadeCooldownTime * 100))}%`;
            rocketCooldownBar.style.width = `${Math.min(100, 100 - (rocketCooldownCounter / rocketCooldownTime * 100))}%`;
            // Update new ability cooldown bars
            repairCooldownBar.style.width = `${Math.min(100, 100 - (trenchRepairAbilityCooldownCounter / trenchRepairAbilityCooldownTime * 100))}%`;
            airstrikeCooldownBar.style.width = `${Math.min(100, 100 - (airstrikeAbilityCooldownCounter / airstrikeAbilityCooldownTime * 100))}%`;
            adrenalineCooldownBar.style.width = `${Math.min(100, 100 - (adrenalineAbilityCooldownCounter / adrenalineAbilityCooldownTime * 100))}%`;

            if (isDeploymentPhase) { deploymentsLeftElement.textContent = deploymentsAvailable; }
        }

        // --- Deployment Phase Logic ---
        function startDeploymentPhase() { isDeploymentPhase = true; deploymentsAvailable = deploymentsPerPhase; deploymentOverlay.style.display = 'block'; canvas.style.cursor = 'copy'; updateUI(); }
        function endDeploymentPhase() { isDeploymentPhase = false; deploymentPlacementPreview = null; deploymentOverlay.style.display = 'none'; canvas.style.cursor = 'crosshair'; waveTransitionCounter = waveTransitionTime; }
        function placeBarbedWire() {
            if (!isDeploymentPhase || deploymentsAvailable <= 0 || !deploymentPlacementPreview) return;
            let validPlacement = true; const newObstacleRect = { x: deploymentPlacementPreview.x, y: deploymentPlacementPreview.y, width: deploymentPlacementPreview.width, height: deploymentPlacementPreview.height };
            for (const obs of obstacles) { if (checkAABBCollision(newObstacleRect, obs)) { validPlacement = false; break; } }
            if (newObstacleRect.y + newObstacleRect.height > canvas.height - trenchHeight - 10) { validPlacement = false; }
            if (validPlacement) { obstacles.push({ x: deploymentPlacementPreview.x, y: deploymentPlacementPreview.y, width: deploymentPlacementPreview.width, height: deploymentPlacementPreview.height }); deploymentsAvailable--; updateUI(); if (toneStarted) { placeWireSound.triggerAttackRelease("C4", "0.1", getNextSoundTime()); } if (deploymentsAvailable <= 0) { endDeploymentPhase(); } } else { console.log("Invalid placement location."); }
        }
        function updateDeployment() { if (!isDeploymentPhase) return; const previewY = Math.max(0, Math.min(mousePos.y - deploymentWireHeight / 2, canvas.height - trenchHeight - deploymentWireHeight - 5)); const previewX = mousePos.x - deploymentWireWidth / 2; deploymentPlacementPreview = { x: previewX, y: previewY, width: deploymentWireWidth, height: deploymentWireHeight }; }

        // --- Upgrade Phase Logic ---
        function startUpgradePhase() {
            isUpgradePhase = true;
            upgradeScoreElement.textContent = score; // Show current score
            // Update button text and disabled state based on cost/score
            for (const type in upgradeBaseCosts) {
                updateUpgradeButton(type);
            }
            skillPointsDisplay.textContent = skillPoints; // Update skill points on upgrade menu button
            upgradeMenu.style.display = 'block';
        }
        function endUpgradePhase() {
            isUpgradePhase = false;
            upgradeMenu.style.display = 'none';
            waveTransitionCounter = waveTransitionTime; // Start transition timer
        }
        function purchaseUpgrade(type) {
            const level = upgradeLevels[type];
            const cost = Math.floor(upgradeBaseCosts[type] * Math.pow(upgradeCostMultiplier, level - 1));

            if (score >= cost) {
                score -= cost;
                upgradeLevels[type]++;
                if (toneStarted) { upgradeSound.triggerAttackRelease("E5", "0.1", getNextSoundTime()); }

                // Apply upgrade effect immediately
                applyUpgrades();

                // Update UI and button states within the upgrade menu
                upgradeScoreElement.textContent = score;
                 // Re-check disable state for all buttons
                 for (const t in upgradeBaseCosts) {
                     updateUpgradeButton(t);
                 }

            }
        }
        function updateUpgradeButton(type) {
             const level = upgradeLevels[type];
             const cost = Math.floor(upgradeBaseCosts[type] * Math.pow(upgradeCostMultiplier, level - 1));
             // Correctly format the ID string (lowercase, no spaces)
             const idSuffix = type.replace(/ /g, '').toLowerCase();
             document.getElementById(`${idSuffix}-level`).textContent = `(Lvl ${level})`;
             document.getElementById(`${idSuffix}-cost`).textContent = cost;
             document.getElementById(`upgrade-${idSuffix}`).disabled = score < cost;
        }
        function applyUpgrades() {
             // Apply effects based on current levels
             currentShootCooldownTime = baseShootCooldownTime * Math.pow(0.9, upgradeLevels.fireRate - 1); // Recalculate base cooldown
             currentPlayerSpeed = basePlayerSpeed * (1 + (upgradeLevels.moveSpeed - 1) * 0.1);
             maxGrenades = 3 + (upgradeLevels.grenadeCap - 1);
             maxRockets = 1 + (upgradeLevels.rocketCap - 1);
             trenchRepairRate = 0.01 * (1 + (upgradeLevels.trenchRepair - 1) * 0.5); // Increase repair rate
             // Update player object directly if needed (like speed)
             playerSpeed = currentPlayerSpeed; // Update global setting used elsewhere
             updateUI(); // Update main UI for grenade/rocket cap if changed
        }

        // --- Skill Tree Logic ---
        function openSkillTree() {
            isSkillTreePhase = true;
            upgradeMenu.style.display = 'none'; // Hide upgrade menu
            skillPointsAvailableElement.textContent = skillPoints;
            for (const skill in skillLevels) {
                updateSkillButton(skill);
            }
            skillTreeMenu.style.display = 'block';
        }

        function closeSkillTree() {
            isSkillTreePhase = false;
            skillTreeMenu.style.display = 'none';
            startUpgradePhase(); // Re-open upgrade menu
        }

        function purchaseSkill(skillName) {
            if (skillPoints > 0 && skillLevels[skillName] < skillMaxLevel) {
                skillPoints--;
                skillLevels[skillName]++;
                if (toneStarted) { skillUnlockSound.triggerAttackRelease("A4", "0.1", getNextSoundTime()); }
                applySkills();
                skillPointsAvailableElement.textContent = skillPoints;
                skillPointsDisplay.textContent = skillPoints; // Update display on upgrade menu button too
                updateSkillButton(skillName);
                // Update other skill buttons as well, in case skill point ran out
                for (const skill in skillLevels) {
                    updateSkillButton(skill);
                }
            }
        }

        function updateSkillButton(skillName) {
            const level = skillLevels[skillName];
            document.getElementById(`${skillName.toLowerCase()}-level`).textContent = `(Lvl ${level})`;
            const button = document.getElementById(`skill-${skillName.toLowerCase()}`);
            if (level >= skillMaxLevel || skillPoints <= 0) {
                button.disabled = true;
                button.querySelector('.skill-cost').textContent = level >= skillMaxLevel ? "MAX" : "1 SP";
            } else {
                button.disabled = false;
                button.querySelector('.skill-cost').textContent = "1 SP";
            }
        }
        function updateSkillPointDisplay() {
            skillPointsDisplay.textContent = skillPoints;
            skillPointsAvailableElement.textContent = skillPoints;
        }

        function applySkills() {
            // Trench Resilience: Increases max trench health
            maxTrenchHealth = 100 + (skillLevels.trenchResilience * 10);
            // Combat Medic: Small passive player health regeneration
            // (Implemented in updatePlayer)
            // Explosives Expert: Increases grenade and rocket damage
            currentGrenadeDamage = baseGrenadeDamage * (1 + skillLevels.explosivesExpert * 0.1);
            currentRocketDamage = baseRocketDamage * (1 + skillLevels.explosivesExpert * 0.1);
            // Rapid Deployment: Reduces ability cooldowns
            const cooldownReductionFactor = 1 - (skillLevels.rapidDeployment * 0.05); // 5% reduction per level
            trenchRepairAbilityCooldownTime = Math.max(120, 600 * cooldownReductionFactor); // Min cooldown 2s
            airstrikeAbilityCooldownTime = Math.max(600, 1800 * cooldownReductionFactor); // Min cooldown 10s
            adrenalineAbilityCooldownTime = Math.max(300, 1200 * cooldownReductionFactor); // Min cooldown 5s

            updateUI(); // To reflect potential trench health change
        }


        // --- Drawing Functions ---
        function drawObstacles() { /* ... (same) ... */ obstacles.forEach(obs => { const wireColor = barbedWireColor; const wireWidth = 1.5; const spacing = 8; for (let x = obs.x; x < obs.x + obs.width; x += spacing) { drawLine(x, obs.y, x + spacing * 0.7, obs.y + obs.height, wireColor, wireWidth); drawLine(x + spacing * 0.7, obs.y, x, obs.y + obs.height, wireColor, wireWidth); } }); }
        function drawNPCs() { // Uses fallback drawing
            friendlyNPCs.forEach(npc => {
                drawDetailedSoldier(npc, npcColor, npcGunColor); // Always use fallback for now
            });
        }
        function drawAmbientNPCs() { // Uses fallback drawing
             ambientNPCs.forEach(npc => {
                 drawDetailedSoldier(npc, ambientNpcColor, npcGunColor, true); // Always use fallback for now
             });
        }
        function drawNPCBullets() { /* ... (same) ... */ npcBullets.forEach(b => drawLine(b.x + b.width/2, b.y, b.x + b.width/2, b.y + b.height, b.color, b.width)); }
        function drawEnemyBullets() { enemyBullets.forEach(b => drawLine(b.x + b.width/2, b.y, b.x + b.width/2, b.y + b.height, b.color, b.width)); }
        function drawMortarShells() { /* ... (includes target marker) ... */ mortarShells.forEach(shell => { drawCircle(shell.x, shell.y, shell.radius, shell.color); const markerAlpha = 0.3 + Math.sin(Date.now() / 200) * 0.2; ctx.strokeStyle = `rgba(255, 0, 0, ${markerAlpha})`; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(shell.x, shell.targetY, mortarRadius * 0.8, 0, Math.PI * 2); ctx.stroke(); }); }
        function drawParticles() { // Added different particle types
            particles.forEach(p => {
                 ctx.fillStyle = p.color;
                 if (p.type === 'spark') { ctx.strokeStyle = p.color; ctx.lineWidth = p.size; ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(p.x - p.dx * 2, p.y - p.dy * 2); ctx.stroke(); }
                 else { drawCircle(p.x, p.y, p.size, p.color); }
            });
        }
        function drawMuzzleFlashes() { /* ... (same) ... */ muzzleFlashes.forEach(flash => { ctx.fillStyle = muzzleFlashColor; ctx.beginPath(); ctx.arc(flash.x, flash.y, flash.size / 2, 0, Math.PI * 2); ctx.fill(); ctx.strokeStyle = muzzleFlashColor; ctx.lineWidth = 2; for (let i = 0; i < 5; i++) { const angle = (i / 5) * Math.PI * 2; const outerX = flash.x + Math.cos(angle) * flash.size; const outerY = flash.y + Math.sin(angle) * flash.size; ctx.beginPath(); ctx.moveTo(flash.x, flash.y); ctx.lineTo(outerX, outerY); ctx.stroke(); } }); }
        function drawGrenades() { grenades.forEach(g => { drawCircle(g.x, g.y, g.radius, g.color); }); }
        function drawRockets() {
             rockets.forEach(r => {
                 drawRect(r.x, r.y, r.width, r.height, r.color);
                 ctx.fillStyle = `rgba(255, ${100 + Math.random()*100}, 0, 0.6)`;
                 drawCircle(r.x + r.width / 2, r.y + r.height + 3, r.width * 0.6);
             });
        }
        function drawExplosions() { // Updated to use explosion color property
             explosions.forEach(exp => { const alpha = exp.life / exp.maxLife; ctx.fillStyle = exp.color.replace(/[\d\.]+\)$/g, `${alpha * 0.8})`); ctx.beginPath(); ctx.arc(exp.x, exp.y, exp.radius * (1 - alpha * 0.5), 0, Math.PI * 2); ctx.fill(); });
        }
        function drawPowerUps() { // Updated to show health/shotgun icon
             powerUps.forEach(p => {
                 ctx.fillStyle = p.color; ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2); ctx.fill();
                 ctx.fillStyle = 'black'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
                 if (p.type === 'rapidFire') { ctx.font = `${p.radius * 1.2}px sans-serif`; ctx.fillText('🔥', p.x, p.y + 1); }
                 else if (p.type === 'reinforcements') { ctx.font = `${p.radius * 1.1}px sans-serif`; ctx.fillText('+', p.x, p.y + 1); }
                 else if (p.type === 'healthKit') { ctx.fillStyle = 'white'; const crossWidth = p.radius * 0.4; const crossLength = p.radius * 1.2; drawRect(p.x - crossLength / 2, p.y - crossWidth / 2, crossLength, crossWidth, 'white'); drawRect(p.x - crossWidth / 2, p.y - crossLength / 2, crossWidth, crossLength, 'white'); }
                 else if (p.type === 'shotgun') { ctx.font = `${p.radius * 1.2}px sans-serif`; ctx.fillText('💥', p.x, p.y + 1); }
             });
        }
        function drawDetailedSoldier(soldier, bodyClr, gunClr, isAmbient = false) { // Added backpack and belt
            const x = soldier.x; const y = soldier.y + (isAmbient ? soldier.animOffset : 0);
            const w = soldier.width; const h = soldier.height;
            const headRadius = w * 0.3; const helmetHeight = headRadius * 1.1; const helmetWidth = headRadius * 2.2; const bodyWidth = w; const bodyHeight = h * 0.6; const legHeight = h * 0.4; const legWidth = bodyWidth * 0.4; const armWidth = w * 0.25; const armLength = h * 0.5; const gunW = soldier.gunWidth; const gunL = soldier.gunLength;
            const headX = x; const headY = y + headRadius; const helmetY = y; const bodyX = x - bodyWidth / 2; const bodyY = y + headRadius * 1.5;
            const legAnimOffset = isAmbient && soldier.legAnimFrame === 0 ? -1 : (isAmbient ? 1 : 0);
            const leftLegX = x - legWidth * 1.1; const rightLegX = x + legWidth * 0.1;
            const leftLegY = bodyY + bodyHeight * 0.8 + (isAmbient ? legAnimOffset : 0);
            const rightLegY = bodyY + bodyHeight * 0.8 - (isAmbient ? legAnimOffset : 0);
            const armY = bodyY + bodyHeight * 0.1; const leftArmX = x - bodyWidth * 0.5 - armWidth; const rightArmX = x + bodyWidth * 0.5; const gunX = x - gunW / 2; const gunY = y - gunL;
            const currentBodyColor = soldier.isHit ? 'rgba(255, 100, 100, 0.8)' : bodyClr; // Hit flash
            drawRect(leftLegX, leftLegY, legWidth, legHeight, currentBodyColor); drawRect(rightLegX, rightLegY, legWidth, legHeight, currentBodyColor); drawRect(bodyX, bodyY, bodyWidth, bodyHeight, currentBodyColor); drawRect(leftArmX, armY, armWidth, armLength, currentBodyColor); drawRect(rightArmX, armY, armWidth, armLength, currentBodyColor);
            // Backpack
            if (!isAmbient) { const packWidth = bodyWidth * 0.7; const packHeight = bodyHeight * 0.6; drawRect(x - packWidth / 2, bodyY + bodyHeight * 0.1, packWidth, packHeight, '#5A5A4A'); }
            // Belt
            if (!isAmbient) { drawRect(bodyX, bodyY + bodyHeight * 0.6, bodyWidth, 3, '#4a3a2a'); }
            if (!isAmbient) { drawRect(gunX, gunY, gunW, gunL, gunClr); }
            drawCircle(headX, headY, headRadius, enemyHeadColor);
            if (soldier.isOfficer) { const capPeakHeight = helmetHeight * 0.4; drawRoundRect(headX - helmetWidth / 2, helmetY, helmetWidth, helmetHeight * 0.8, helmetHeight * 0.3, officerCapColor); drawRect(headX - helmetWidth / 2, helmetY + helmetHeight * 0.8 - capPeakHeight, helmetWidth, capPeakHeight, officerCapColor); }
            else { drawRoundRect(headX - helmetWidth / 2, helmetY, helmetWidth, helmetHeight, helmetHeight * 0.4, enemyHelmetColor); }
            if (soldier.isOfficer) { ctx.strokeStyle = 'rgba(255, 215, 0, 0.4)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, y + h / 2, officerBuffRadius * 0.15, 0, Math.PI * 2); ctx.stroke(); }
        }
        function drawEnemy(enemy) { // Added arm animation
            const x = enemy.x; const y = enemy.y; const w = enemy.width; const h = enemy.height;
            // Draw Shadow
            ctx.fillStyle = 'rgba(0, 0, 0, 0.2)'; ctx.beginPath(); ctx.ellipse(x + w / 2, y + h + 3, w * 0.6, 4, 0, 0, Math.PI * 2); ctx.fill();
            // Proportions & Positions
            const headRadius = w * 0.2; const helmetHeight = headRadius * 1.1; const helmetWidth = headRadius * 2.2; const bodyWidth = w * 0.8; const bodyHeight = h * 0.5; const legHeight = h * 0.35; const legWidth = bodyWidth * 0.4; const armWidth = w * 0.2; const armLength = h * 0.4; const gunLength = w * 1.2; const gunHeight = h * 0.1;
            const headX = x + w / 2; const headY = y + headRadius; const helmetY = y; const bodyX = x + (w - bodyWidth) / 2; const bodyY = y + headRadius * 2;
            // Leg & Arm Animation Offset
            const animProgress = enemy.legAnimTimer / (enemyAnimSpeed / (enemy.currentSpeed / enemy.baseSpeed + 0.01)); // Normalize anim progress (prevent division by zero)
            const legAnimOffset = Math.sin(animProgress * Math.PI) * 3; // Back and forth swing for legs
            const armAnimOffset = Math.cos(animProgress * Math.PI) * enemyArmSwingAngle; // Opposite swing for arms (angle)

            const leftLegX = bodyX; const rightLegX = bodyX + bodyWidth - legWidth;
            const leftLegY = bodyY + bodyHeight + legAnimOffset; // Apply offset
            const rightLegY = bodyY + bodyHeight - legAnimOffset; // Apply opposite offset
            const armY = bodyY + bodyHeight * 0.1;
            const leftArmX = bodyX - armWidth; const rightArmX = bodyX + bodyWidth;
            const gunX = bodyX + bodyWidth / 2; const gunY = bodyY + bodyHeight * 0.3;
            // Draw parts
            drawRect(leftLegX, leftLegY, legWidth, legHeight, enemy.bodyColor); drawRect(rightLegX, rightLegY, legWidth, legHeight, enemy.bodyColor);
            drawRect(bodyX, bodyY, bodyWidth, bodyHeight, enemy.bodyColor);
            // Draw Arms with Rotation
            ctx.save(); ctx.translate(leftArmX + armWidth / 2, armY); ctx.rotate(-armAnimOffset); drawRect(-armWidth / 2, 0, armWidth, armLength, enemy.bodyColor); ctx.restore();
            ctx.save(); ctx.translate(rightArmX + armWidth / 2, armY); ctx.rotate(armAnimOffset); drawRect(-armWidth / 2, 0, armWidth, armLength, enemy.bodyColor); ctx.restore();

            if (enemy.type === 'mortar') { const mortarTubeWidth = w * 0.3; const mortarTubeLength = h * 0.6; ctx.save(); ctx.translate(x + w / 2, y + h * 0.6); ctx.rotate(-0.8); drawRect(-mortarTubeWidth / 2, -mortarTubeLength, mortarTubeWidth, mortarTubeLength, enemyGunColor); ctx.restore(); }
            else if (enemy.type !== 'shield') { drawRect(gunX - gunLength / 2, gunY, gunLength, gunHeight, enemyGunColor); }
            drawCircle(headX, headY, headRadius, enemy.headColor); drawRoundRect(headX - helmetWidth / 2, helmetY, helmetWidth, helmetHeight, helmetHeight * 0.4, enemyHelmetColor);
            // Draw Shield
            if (enemy.type === 'shield') { const shieldWidth = w * 1.4; const shieldHeight = h * 0.8; drawRoundRect(x + w / 2 - shieldWidth / 2, y + h * 0.1, shieldWidth, shieldHeight, 5, shieldEnemyColor); ctx.strokeStyle = '#444'; ctx.lineWidth = 1; ctx.strokeRect(x + w / 2 - shieldWidth / 2, y + h * 0.1, shieldWidth, shieldHeight); }
            // Health Bar
            if (enemy.health < enemy.maxHealth) { const barWidth = w * 0.8; const barHeight = 4; const barX = x + (w - barWidth) / 2; const barY = y - barHeight - 2; const healthPercent = enemy.health / enemy.maxHealth; drawRect(barX, barY, barWidth, barHeight, '#555'); drawRect(barX, barY, barWidth * healthPercent, barHeight, '#dc3545'); }
            // Draw Commander Aura
            if (enemy.type === 'commander' && enemy.state === 'buffing') { ctx.strokeStyle = 'rgba(255, 215, 0, 0.3)'; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(x + w / 2, y + h / 2, commanderBuffRadius * 0.8, 0, Math.PI * 2); ctx.stroke(); }
             // Draw Medic Heal Pulse
             if (enemy.type === 'medic' && enemy.state === 'healing' && enemy.healCooldown < 30) { ctx.fillStyle = 'rgba(0, 255, 0, 0.15)'; ctx.beginPath(); ctx.arc(x + w / 2, y + h / 2, medicHealRadius * (1 - enemy.healCooldown/30), 0, Math.PI * 2); ctx.fill(); }
        }
        function drawBackgroundDetails() { // Added more details
             backgroundDetails.forEach(detail => {
                 ctx.save();
                 ctx.translate(detail.x, detail.y);
                 ctx.rotate(detail.angle);
                 if (detail.type === 'plank') {
                     drawRect(-detail.width / 2, -detail.height / 2, detail.width, detail.height, detail.color);
                 } else if (detail.type === 'rock') {
                      ctx.fillStyle = detail.color; ctx.beginPath(); ctx.moveTo(-detail.width / 2, detail.height / 2); ctx.lineTo(-detail.width / 3, -detail.height / 3); ctx.lineTo(0, -detail.height / 2); ctx.lineTo(detail.width / 3, -detail.height / 4); ctx.lineTo(detail.width / 2, detail.height / 2); ctx.closePath(); ctx.fill();
                 } else if (detail.type === 'crater') {
                     drawCircle(0, 0, detail.width / 2, detail.color);
                 }
                 ctx.restore();
             });
        }
        function drawTrenchDetails() {
             const trenchTopY = backTrenchY + playerHeight; // Use backTrenchY for details
             // Boxes
             ctx.fillStyle = '#8B4513'; drawRect(canvas.width * 0.1, trenchTopY - 20, 25, 20, '#8B4513'); drawRect(canvas.width * 0.12, trenchTopY - 25, 20, 15, '#A0522D'); drawRect(canvas.width * 0.85, trenchTopY - 15, 30, 25, '#8B4513');
             // Gun Rack
             ctx.strokeStyle = '#555'; ctx.lineWidth = 2; const rackX = canvas.width * 0.6; const rackY = trenchTopY - 25; const rackH = 30; const rackW = 5; drawLine(rackX, rackY, rackX, rackY + rackH, '#555', 3); drawLine(rackX + rackW * 3, rackY, rackX + rackW*3, rackY + rackH, '#555', 3); drawLine(rackX, rackY + rackH * 0.3, rackX + rackW*3, rackY + rackH * 0.3, '#555', 2); drawLine(rackX, rackY + rackH * 0.7, rackX + rackW*3, rackY + rackH * 0.7, '#555', 2);
             // Tent
             ctx.fillStyle = '#BDB76B'; ctx.beginPath(); ctx.moveTo(canvas.width * 0.4, trenchTopY - 30); ctx.lineTo(canvas.width * 0.4 + 30, trenchTopY); ctx.lineTo(canvas.width * 0.4 - 30, trenchTopY); ctx.closePath(); ctx.fill();
             // Add simple helmet shape
             ctx.fillStyle = enemyHelmetColor; ctx.beginPath(); ctx.arc(canvas.width * 0.15, backTrenchY + playerHeight - 5, 8, 0, Math.PI, true); ctx.fill();
        }
        function drawDeploymentPreview() { /* ... (same) ... */ if (isDeploymentPhase && deploymentPlacementPreview && deploymentsAvailable > 0) { ctx.globalAlpha = 0.5; const obs = deploymentPlacementPreview; const wireColor = barbedWireColor; const wireWidth = 1.5; const spacing = 8; for (let x = obs.x; x < obs.x + obs.width; x += spacing) { drawLine(x, obs.y, x + spacing * 0.7, obs.y + obs.height, wireColor, wireWidth); drawLine(x + spacing * 0.7, obs.y, x, obs.y + obs.height, wireColor, wireWidth); } ctx.globalAlpha = 1.0; } }
        function drawClouds() {
             ctx.fillStyle = cloudColor;
             clouds.forEach(cloud => {
                 drawCircle(cloud.x, cloud.y, cloud.size * 0.6, cloudColor);
                 drawCircle(cloud.x + cloud.size * 0.4, cloud.y + cloud.size * 0.1, cloud.size * 0.5, cloudColor);
                 drawCircle(cloud.x - cloud.size * 0.3, cloud.y + cloud.size * 0.2, cloud.size * 0.4, cloudColor);
             });
        }
        function drawHitMarkers() {
             ctx.strokeStyle = hitMarkerColor;
             ctx.lineWidth = 2;
             hitMarkers.forEach(marker => {
                 const size = hitMarkerSize * (marker.life / hitMarkerLife); // Shrink as it fades
                 ctx.globalAlpha = marker.life / hitMarkerLife; // Fade out
                 ctx.beginPath();
                 ctx.moveTo(marker.x - size / 2, marker.y - size / 2);
                 ctx.lineTo(marker.x + size / 2, marker.y + size / 2);
                 ctx.moveTo(marker.x + size / 2, marker.y - size / 2);
                 ctx.lineTo(marker.x - size / 2, marker.y + size / 2);
                 ctx.stroke();
             });
             ctx.globalAlpha = 1.0; // Reset alpha
        }


        function drawGameObjects() {
            // --- Draw Static Background FIRST (Unaffected by shake) ---
            drawBackgroundDetails();
            const wallColor = '#5a4a3a'; // Color for trench wall
            const sandbagColor = '#C19A6B'; const sandbagColorDark = '#A17A4B';
            const sandbagHeight = 12; const sandbagWidth = 25;
            const healthPercent = trenchHealth / maxTrenchHealth;

            // Draw Back Trench Wall & Floor
            drawRect(0, backTrenchY + playerHeight, canvas.width, canvas.height - (backTrenchY + playerHeight), wallColor);
            // Add vertical support beams to back trench wall
            ctx.fillStyle = '#4a3a2a'; // Darker brown for beams
            for(let i = 0; i < 5; i++) {
                drawRect(canvas.width * (0.1 + i * 0.2), backTrenchY + playerHeight, 10, canvas.height - (backTrenchY + playerHeight), '#4a3a2a');
            }
            // Draw top line of the trench wall (defines the edge)
            drawLine(0, backTrenchY + playerHeight, canvas.width, backTrenchY + playerHeight, '#4B3A2A', 2);

            // Draw the dirt texture between sandbags and floor (this is the visible part of the trench wall)
            drawRect(0, backTrenchY + sandbagHeight, canvas.width, playerHeight - sandbagHeight, wallColor);


            // Draw Back Trench Details (Props like boxes, tent)
            drawTrenchDetails();

            // Draw Sandbags (Back Trench - Damaged)
            for (let x = -sandbagWidth / 3; x < canvas.width; x += sandbagWidth * 0.7) { if (Math.random() < healthPercent * 0.7 + 0.15) { const yOffset = (1 - healthPercent) * (Math.random() * 6 - 3); const damageFactor = (1 - healthPercent) * 0.6; const r = Math.max(0, parseInt(sandbagColor.substring(1, 3), 16) * (1 - damageFactor)); const g = Math.max(0, parseInt(sandbagColor.substring(3, 5), 16) * (1 - damageFactor)); const b = Math.max(0, parseInt(sandbagColor.substring(5, 7), 16) * (1 - damageFactor)); const damagedColor = `rgb(${Math.floor(r)}, ${Math.floor(g)}, ${Math.floor(b)})`; const damagedColorDark = `rgb(${Math.floor(r*0.8)}, ${Math.floor(g*0.8)}, ${Math.floor(b*0.8)})`; ctx.fillStyle = damagedColorDark; ctx.beginPath(); if (ctx.roundRect) { ctx.roundRect(x, backTrenchY + 2 + yOffset, sandbagWidth, sandbagHeight, 5); } else { ctx.rect(x, backTrenchY + 2 + yOffset, sandbagWidth, sandbagHeight); } ctx.fill(); ctx.fillStyle = damagedColor; ctx.beginPath(); if (ctx.roundRect) { ctx.roundRect(x, backTrenchY + yOffset, sandbagWidth, sandbagHeight, 5); } else { ctx.rect(x, backTrenchY + yOffset, sandbagWidth, sandbagHeight); } ctx.fill(); } }

            // Draw Clouds (Also static relative to shake)
            drawClouds();

            // --- Apply Screen Shake FOR GAMEPLAY ELEMENTS ONLY ---
            const shakeX = (Math.random() - 0.5) * screenShakeMagnitude * 2;
            const shakeY = (Math.random() - 0.5) * screenShakeMagnitude * 2;
            ctx.save();
            ctx.translate(shakeX, shakeY);

            // --- Draw Gameplay Elements (Affected by shake) ---
            drawAmbientNPCs();
            drawNPCs();
            drawObstacles();
            drawPowerUps();
            drawPlayer();
            bullets.forEach(b => drawLine(b.x + b.width/2, b.y, b.x + b.width/2, b.y + b.height, b.color, b.width));
            drawNPCBullets();
            drawEnemyBullets();
            drawMortarShells();
            drawGrenades();
            drawRockets();
            enemies.forEach(enemy => { drawEnemy(enemy); });

            // --- Draw Effects & Overlays (Affected by shake) ---
            drawParticles();
            drawMuzzleFlashes();
            drawExplosions();
            drawHitMarkers();
            drawDeploymentPreview();

            ctx.restore(); // Restore from shake
        }

        function drawPlayer() { // Uses fallback drawing
             drawDetailedSoldier(player, player.color, player.gunColor);
        }

        // --- Game State Management ---
        function togglePause() { if (gameOver || isDeploymentPhase || isUpgradePhase || isSkillTreePhase) return; isPaused = !isPaused; if (isPaused) { cancelAnimationFrame(animationFrameId); pauseMenu.style.display = 'block'; } else { pauseMenu.style.display = 'none'; requestAnimationFrame(gameLoop); } }
        function triggerGameOver() { /* ... (same) ... */ gameOver = true; gameRunning = false; cancelAnimationFrame(animationFrameId); messageTitle.textContent = "Position Overrun!"; messageText.textContent = `Your final score is ${score}.`; messageBox.style.display = 'block'; }
        function restartGame(fromPauseMenu = false) {
            if(fromPauseMenu) { isPaused = false; pauseMenu.style.display = 'none'; }
            score = 0; playerHealth = 100; trenchHealth = maxTrenchHealth; // Reset trench health
            gameOver = false; gameRunning = true; isDeploymentPhase = false; isUpgradePhase = false; isSkillTreePhase = false;
            bullets = []; npcBullets = []; enemyBullets = []; mortarShells = []; rockets = []; enemies = []; obstacles = []; friendlyNPCs = []; ambientNPCs = []; clouds = [];
            particles = []; muzzleFlashes = []; grenades = []; explosions = []; powerUps = []; hitMarkers = [];
            player.x = canvas.width / 2; playerPowerUp = { type: null, timer: 0 }; // Removed player.currentTrench reset
            enemySpawnCounter = 0; shootCooldownCounter = 0; grenadeCooldownCounter = 0; rocketCooldownCounter = 0;
            trenchRepairAbilityCooldownCounter = 0; airstrikeAbilityCooldownCounter = 0; adrenalineAbilityCooldownCounter = 0; // Reset ability cooldowns
            currentWave = 0; waveTransitionCounter = 0; // Start deployment immediately
            grenadeCount = 3; rocketCount = 1;
            skillPoints = 0; // Reset skill points
            skillLevels = { trenchResilience: 0, combatMedic: 0, explosivesExpert: 0, rapidDeployment: 0 };
            applySkills(); // Apply base skill effects
            screenShakeDuration = 0; screenShakeMagnitude = 0; deploymentsAvailable = 0; deploymentPlacementPreview = null;
            // Reset upgrades
            upgradeLevels = { fireRate: 1, moveSpeed: 1, grenadeCap: 1, rocketCap: 1, trenchRepair: 1 };
            applyUpgrades(); // Apply base stats
            keys.ArrowLeft = false; keys.ArrowRight = false; keys.Space = false; keys.KeyG = false; keys.KeyP = false; keys.KeyR = false; keys.KeyF = false; keys.KeyA = false; keys.KeyD = false; keys.KeyW = false; keys.KeyS = false; // Reset all keys
            touchLeft = false; touchRight = false; touchShoot = false; touchGrenade = false; touchRocket = false; touchRepair = false; touchAirstrike = false; touchAdrenaline = false; touchUp = false; touchDown = false;
            initializeObstacles(); initializeNPCs(); initializeAmbientNPCs(); initializeBackgroundDetails(); initializeClouds();
            messageBox.style.display = 'none'; deploymentOverlay.style.display = 'none'; upgradeMenu.style.display = 'none'; skillTreeMenu.style.display = 'none';
            updateUI();
            cancelAnimationFrame(animationFrameId);
            startDeploymentPhase(); // Start with deployment phase
            gameLoop();
        }

        // --- Initialization and Resizing ---
        let backgroundDetails = [];
        function initializeBackgroundDetails() { // Added more detail types
             backgroundDetails = [];
             backgroundDetails.push({ type: 'plank', x: canvas.width * 0.3, y: canvas.height * 0.2, width: 60, height: 10, angle: 0.2, color: '#8B4513' });
             backgroundDetails.push({ type: 'plank', x: canvas.width * 0.7, y: canvas.height * 0.35, width: 80, height: 8, angle: -0.1, color: '#8B4513' });
             backgroundDetails.push({ type: 'rock', x: canvas.width * 0.1, y: canvas.height * 0.5, width: 30, height: 20, angle: 0.5, color: '#696969'});
             backgroundDetails.push({ type: 'rock', x: canvas.width * 0.9, y: canvas.height * 0.6, width: 40, height: 25, angle: -0.3, color: '#778899'});
             backgroundDetails.push({ type: 'crater', x: canvas.width * 0.5, y: canvas.height * 0.15, width: 50, height: 0, angle: 0, color: 'rgba(0,0,0,0.15)'}); // Crater shadow
             backgroundDetails.push({ type: 'crater', x: canvas.width * 0.2, y: canvas.height * 0.45, width: 40, height: 0, angle: 0, color: 'rgba(0,0,0,0.1)'});
        }
        function drawBackgroundDetails() { /* ... (includes drawing rocks/craters) ... */ backgroundDetails.forEach(detail => { ctx.save(); ctx.translate(detail.x, detail.y); ctx.rotate(detail.angle); if (detail.type === 'plank') { drawRect(-detail.width / 2, -detail.height / 2, detail.width, detail.height, detail.color); } else if (detail.type === 'rock') { ctx.fillStyle = detail.color; ctx.beginPath(); ctx.moveTo(-detail.width / 2, detail.height / 2); ctx.lineTo(-detail.width / 3, -detail.height / 3); ctx.lineTo(0, -detail.height / 2); ctx.lineTo(detail.width / 3, -detail.height / 4); ctx.lineTo(detail.width / 2, detail.height / 2); ctx.closePath(); ctx.fill(); } else if (detail.type === 'crater') { drawCircle(0, 0, detail.width / 2, detail.color); } ctx.restore(); }); }

        function initializeObstacles() { /* ... (same) ... */ obstacles = []; obstacles.push({ x: canvas.width * 0.15, y: canvas.height * 0.4, width: canvas.width * 0.2, height: 30 }); obstacles.push({ x: canvas.width * 0.65, y: canvas.height * 0.55, width: canvas.width * 0.25, height: 25 }); obstacles.push({ x: canvas.width * 0.40, y: canvas.height * 0.25, width: canvas.width * 0.15, height: 20 }); }
        function initializeNPCs() { // Designate one as officer
            friendlyNPCs = [];
            initializeSingleNPC(canvas.width * 0.25, true); // Add first NPC as officer
            initializeSingleNPC(canvas.width * 0.75, false); // Add second NPC
            updateUI();
        }
        function initializeSingleNPC(posX, isOfficer = false) { // Added movement properties & hit state
             const npcWidth = 28; const npcHeight = 38;
             const npcBaseY = backTrenchY; // Use calculated back trench Y
             const npcGunWidth = player.gunWidth * 0.8; const npcGunLength = player.gunLength * 0.8;
             // Assign slightly varied colors
             const baseColorVal = parseInt(npcColor.substring(1), 16);
             const r = Math.max(0, Math.min(255, ((baseColorVal >> 16) & 0xFF) + Math.floor(Math.random()*20-10)));
             const g = Math.max(0, Math.min(255, ((baseColorVal >> 8) & 0xFF) + Math.floor(Math.random()*20-10)));
             const b = Math.max(0, Math.min(255, (baseColorVal & 0xFF) + Math.floor(Math.random()*20-10)));
             const variedNpcColor = `rgb(${r},${g},${b})`;

             friendlyNPCs.push({
                 x: posX, y: npcBaseY, initialX: posX,
                 width: npcWidth, height: npcHeight, color: variedNpcColor, // Use varied color
                 gunWidth: npcGunWidth, gunLength: npcGunLength, gunColor: npcGunColor,
                 shootCooldown: Math.random() * npcShootCooldownVariance + 60,
                 moveCooldown: Math.random() * npcMoveCooldown, targetX: posX,
                 health: npcHealth, isOfficer: isOfficer,
                 isHit: false, hitTimer: 0,
             });
        }
        function initializeAmbientNPCs() { /* ... (same) ... */
             ambientNPCs = []; const numAmbient = 3; for (let i = 0; i < numAmbient; i++) { const npcWidth = 24; const npcHeight = 30; const npcBaseY = canvas.height - trenchHeight + (trenchHeight * 0.6) - npcHeight; const startX = Math.random() * canvas.width; ambientNPCs.push({ x: startX, y: npcBaseY, width: npcWidth, height: npcHeight, color: ambientNpcColor, gunWidth: 0, gunLength: 0, speed: ambientNpcSpeed * (Math.random() * 0.4 + 0.8), targetX: Math.random() * canvas.width, animOffset: 0, animPhase: Math.random() * Math.PI * 2, legAnimFrame: 0, legAnimTimer: 0 }); }
        }
        function initializeClouds() {
             clouds = [];
             for (let i = 0; i < numClouds; i++) {
                 clouds.push({
                     x: Math.random() * canvas.width,
                     y: Math.random() * (canvas.height * 0.2),
                     size: Math.random() * 40 + 30,
                     speed: cloudMinSpeed + Math.random() * (cloudMaxSpeed - cloudMinSpeed)
                 });
             }
        }
        function updateClouds() {
             clouds.forEach(cloud => {
                 cloud.x += cloud.speed * (adrenalineActive ? adrenalineSlowFactor * 0.5 : 1); // Slow clouds slightly during adrenaline
                 if (cloud.x - cloud.size > canvas.width) {
                     cloud.x = -cloud.size * 1.5;
                     cloud.y = Math.random() * (canvas.height * 0.2);
                 }
             });
        }

        function resizeCanvas() {
            const container = canvas.parentElement; const maxWidth = container.clientWidth > 0 ? container.clientWidth * 0.95 : 1100; const maxHeight = window.innerHeight > 0 ? window.innerHeight * 0.80 : 600; /* Increased max height */ let newWidth = maxWidth, newHeight = newWidth / (16 / 10); if (newHeight > maxHeight) { newHeight = maxHeight; newWidth = newHeight * (16 / 10); } newWidth = Math.max(newWidth, 320); newHeight = Math.max(newHeight, 200); canvas.width = newWidth; canvas.height = newHeight;
            // Recalculate trench positions based on new height
            backTrenchY = canvas.height - trenchHeight + (trenchHeight / 3) - playerHeight;
            // forwardTrenchY = canvas.height - trenchHeight - trenchSpacing - playerHeight; // Removed forward trench calculation
            // Update player Y based on current trench (always back now)
            player.y = backTrenchY;
            // Recenter player X
            const halfWidth = player.width / 2; player.x = Math.max(halfWidth, Math.min(canvas.width - halfWidth, player.x));

            initializeObstacles(); initializeNPCs(); initializeAmbientNPCs(); initializeBackgroundDetails(); initializeClouds(); // Init clouds on resize
            if (ctx && (gameRunning || gameOver) && !isPaused && !isDeploymentPhase && !isUpgradePhase) { clearCanvas(); drawGameObjects(); } // Avoid redraw if paused/deploying/upgrading
        }

        // --- Game Loop ---
        function gameLoop() {
            if (isPaused || !gameRunning || isSkillTreePhase) { // Also pause game loop if skill tree is open
                 if (isSkillTreePhase) { // Keep drawing static background if skill tree is open
                    clearCanvas();
                    drawGameObjects(); // This will draw static elements, then skip dynamic ones due to shake logic
                 }
                return;
            }

            clearCanvas(); // Draws background layers

            // Updates
            if (!isDeploymentPhase && !isUpgradePhase && waveTransitionCounter <= 0) { // Check upgrade phase
                updatePlayer(); updateNPCs(); updateAmbientNPCs();
                updateBullets(); updateNPCBullets(); updateEnemyBullets();
                updateEnemies(); updateGrenades(); updatePowerUps(); updateMortarShells(); updateRockets();
                updateHitMarkers(); // Update hit markers
                updateAirstrike(); updateAdrenaline(); // Update abilities
                handleCollisions();
            } else if (isDeploymentPhase) {
                 updateDeployment();
            } else if (isUpgradePhase) {
                 // No updates needed while upgrade menu is shown, handled by events
            }
            updateWaves(); updateParticles(); updateMuzzleFlashes(); updateExplosions(); updateScreenShake(); updateClouds();

            // Drawing
            drawGameObjects();

            animationFrameId = requestAnimationFrame(gameLoop);
        }

        // --- Initialization ---
        // loadAllImages(); // Removed image loading
        window.addEventListener('resize', resizeCanvas);
        restartButton.addEventListener('click', () => restartGame(false));
        resumeButton.addEventListener('click', togglePause);
        restartPauseButton.addEventListener('click', () => restartGame(true));
        finishDeploymentButton.addEventListener('click', endDeploymentPhase);
        // Add event listeners for upgrade buttons
        document.getElementById('upgrade-firerate').addEventListener('click', () => purchaseUpgrade('fireRate'));
        document.getElementById('upgrade-movespeed').addEventListener('click', () => purchaseUpgrade('moveSpeed'));
        document.getElementById('upgrade-grenadecap').addEventListener('click', () => purchaseUpgrade('grenadeCap'));
        document.getElementById('upgrade-rocketcap').addEventListener('click', () => purchaseUpgrade('rocketCap'));
        document.getElementById('upgrade-trenchrepair').addEventListener('click', () => purchaseUpgrade('trenchRepair'));
        continueButton.addEventListener('click', endUpgradePhase);
        // Skill Tree Buttons
        skillTreeButton.addEventListener('click', openSkillTree);
        closeSkillTreeButton.addEventListener('click', closeSkillTree);
        document.getElementById('skill-trenchresilience').addEventListener('click', () => purchaseSkill('trenchResilience'));
        document.getElementById('skill-combatmedic').addEventListener('click', () => purchaseSkill('combatMedic'));
        document.getElementById('skill-explosivesexpert').addEventListener('click', () => purchaseSkill('explosivesExpert'));
        document.getElementById('skill-rapiddeployment').addEventListener('click', () => purchaseSkill('rapidDeployment'));


        resizeCanvas(); // Initial size & setup
        applyUpgrades(); // Apply initial stats based on level 1
        applySkills(); // Apply initial skill effects
        updateUI();
        startDeploymentPhase(); // Start with deployment phase
        // Wait a short moment before starting loop
        setTimeout(gameLoop, 50);

    </script>

</body>
</html>
