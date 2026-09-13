// Backend API base URL. When FastAPI serves this frontend, use the same origin.
const API_BASE_URL = window.location.port === '8000'
    ? window.location.origin
    : 'http://localhost:8000';

let CURRENT_USER = {
    id: 'athlete',
    name: 'Athlete',
    avatar: 'https://ui-avatars.com/api/?name=Athlete&background=0D8ABC&color=fff'
};

function setUserProfile(user = CURRENT_USER) {
    const userNameEl = document.getElementById('user-name');
    const userAvatarEl = document.getElementById('user-avatar');

    if (userNameEl) {
        userNameEl.innerText = user.name;
    }
    if (userAvatarEl) {
        userAvatarEl.src = user.avatar;
    }
}

// User selector handler
const userDropdown = document.getElementById('user-dropdown');
if (userDropdown) {
    userDropdown.addEventListener('change', async (e) => {
        const userId = e.target.value;
        CURRENT_USER.id = userId;
        await loadAnalytics();
    });
}

// Navigation Logic
const navItems = document.querySelectorAll('.nav-links li');
const views = document.querySelectorAll('.view');

navItems.forEach(item => {
    item.addEventListener('click', () => {
        // Remove active from all nav
        navItems.forEach(nav => nav.classList.remove('active'));
        // Add active to clicked
        item.classList.add('active');

        // Hide all views
        views.forEach(view => view.classList.remove('active-view'));
        // Show target view
        const targetId = item.getAttribute('data-target');
        document.getElementById(targetId).classList.add('active-view');
    });
});

// Utility functions for UI feedback
function showNotification(message, type = 'success', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, duration);
}

function setLoading(button, loading = true) {
    if (loading) {
        button.classList.add('btn-loading');
        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
    } else {
        button.classList.remove('btn-loading');
        button.disabled = false;
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
        }
    }
}

function shakeElement(element) {
    element.classList.add('shake');
    setTimeout(() => element.classList.remove('shake'), 500);
}

// Dietician Logic
const dietForm = document.getElementById('diet-form');
const dietResult = document.getElementById('diet-result');

dietForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = dietForm.querySelector('button[type="submit"]');
    setLoading(submitBtn, true);

    const age = parseInt(document.getElementById('age').value);
    const weight = parseFloat(document.getElementById('weight').value);
    const height = parseFloat(document.getElementById('height').value);
    const goal = document.getElementById('goal').value;

    // Basic validation
    if (age < 10 || age > 120) {
        showNotification('Please enter a valid age (10-120)', 'error');
        shakeElement(document.getElementById('age'));
        setLoading(submitBtn, false);
        return;
    }

    if (weight < 30 || weight > 300) {
        showNotification('Please enter a valid weight (30-300 kg)', 'error');
        shakeElement(document.getElementById('weight'));
        setLoading(submitBtn, false);
        return;
    }

    if (height < 100 || height > 250) {
        showNotification('Please enter a valid height (100-250 cm)', 'error');
        shakeElement(document.getElementById('height'));
        setLoading(submitBtn, false);
        return;
    }

    const payload = {
        age: age,
        weight_kg: weight,
        height_cm: height,
        goal: goal
    };

    try {
        const response = await fetch(`${API_BASE_URL}/api/dietician/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if(response.ok) {
            const data = await response.json();

            document.getElementById('res-bmi').innerText = data.bmi;
            document.getElementById('res-bmi-category').innerText = data.bmi_category || 'N/A';
            document.getElementById('res-cal').innerText = `${data.recommended_calories} kcal`;
            document.getElementById('res-maintenance').innerText = `${data.maintenance_calories} kcal maintenance`;
            document.getElementById('res-plan').innerText = data.plan_summary;

            document.getElementById('res-protein').innerText = `${data.macros?.protein_g ?? '--'} g`;
            document.getElementById('res-carbs').innerText = `${data.macros?.carbs_g ?? '--'} g`;
            document.getElementById('res-fat').innerText = `${data.macros?.fat_g ?? '--'} g`;

            const mealListEl = document.getElementById('res-meal-list');
            mealListEl.innerHTML = '';
            (data.sample_meals || []).forEach((item, index) => {
                const li = document.createElement('li');
                li.innerText = item;
                li.style.animationDelay = `${index * 0.1}s`;
                li.classList.add('slide-up');
                mealListEl.appendChild(li);
            });

            const listEl = document.getElementById('res-grocery-list');
            listEl.innerHTML = '';
            (data.grocery_list || []).forEach((item, index) => {
                const li = document.createElement('li');
                li.innerText = item;
                li.style.animationDelay = `${index * 0.1}s`;
                li.classList.add('slide-up');
                listEl.appendChild(li);
            });

            dietResult.style.display = 'block';
            dietResult.classList.add('fade-in');
            showNotification('Diet plan generated successfully!', 'success');
        } else {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            showNotification(`Error: ${errorData.detail}`, 'error');
            shakeElement(dietForm);
        }

    } catch (err) {
        console.error("Fetch error:", err);
        showNotification("Failed to connect to the backend. Make sure the FastAPI server is running.", 'error');
        shakeElement(dietForm);
    } finally {
        setLoading(submitBtn, false);
    }
});

// AI Trainer / Camera Logic
const video = document.getElementById('webcam');
const canvas = document.getElementById('overlay');
const ctx = canvas.getContext('2d');
const startBtn = document.getElementById('start-camera');
const stopBtn = document.getElementById('stop-camera');
const formAngleEl = document.getElementById('form-angle');
const repCountEl = document.getElementById('rep-count');
const feedbackMsgEl = document.getElementById('ai-feedback-msg');

let isStreaming = false;
let stream = null;
let captureInterval = null;
let repCount = 0;
let lastStage = "down"; // To track curls

startBtn.addEventListener('click', async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        video.style.display = 'block';
        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline-block';
        isStreaming = true;
        
        // Match canvas size to video
        video.onloadedmetadata = () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
        };

        // Start sending frames to backend
        captureInterval = setInterval(sendFrameToBackend, 500); // 2 FPS for performance
        
    } catch (err) {
        console.error("Camera error:", err);
        alert("Could not access the camera.");
    }
});

stopBtn.addEventListener('click', () => {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
    video.style.display = 'none';
    startBtn.style.display = 'inline-block';
    stopBtn.style.display = 'none';
    isStreaming = false;
    clearInterval(captureInterval);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    feedbackMsgEl.innerText = "Waiting for movement...";
});

async function sendFrameToBackend() {
    if (!isStreaming) return;

    // Draw current video frame to a temporary canvas to get blob
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = video.videoWidth;
    tempCanvas.height = video.videoHeight;
    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);

    tempCanvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append('file', blob, 'frame.jpg');

        try {
            const response = await fetch(`${API_BASE_URL}/api/trainer/analyze-pose`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                handlePoseResponse(data);
            }
        } catch (err) {
            console.error("Error sending frame:", err);
            // Optionally update UI for connection error
        }
    }, 'image/jpeg', 0.7);
}

function handlePoseResponse(data) {
    if (data.status === 'success' && data.pose_detected) {
        formAngleEl.innerText = `${data.angle}°`;
        feedbackMsgEl.innerText = data.feedback;
        
        // Rep counting logic
        if (data.stage === "up" && lastStage === "down") {
            repCount += 1;
            repCountEl.innerText = repCount;
            // Add a little pop animation class (optional)
            repCountEl.classList.add('pop');
            setTimeout(() => repCountEl.classList.remove('pop'), 300);
        }
        
        if (data.stage === "down" || data.stage === "up") {
            lastStage = data.stage;
        }

        // Draw landmarks
        drawLandmarks(data.landmarks);
    } else {
        feedbackMsgEl.innerText = "No pose detected. Step back.";
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
}

function drawLandmarks(landmarks) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Set style
    ctx.fillStyle = "#10b981"; // Success green color
    ctx.strokeStyle = "#3b82f6"; // Primary blue color
    ctx.lineWidth = 2;

    // Define pose connections (simplified skeleton)
    const connections = [
        // Torso
        [11, 12], [11, 23], [12, 24], [23, 24],
        // Left arm
        [11, 13], [13, 15],
        // Right arm  
        [12, 14], [14, 16],
        // Left leg
        [23, 25], [25, 27], [27, 29], [29, 31],
        // Right leg
        [24, 26], [26, 28], [28, 30], [30, 32],
        // Face (simplified)
        [0, 1], [1, 2], [2, 3], [3, 7],
        [0, 4], [4, 5], [5, 6], [6, 8],
        [9, 10]
    ];

    // Draw connections first
    ctx.strokeStyle = "#3b82f6";
    ctx.lineWidth = 3;
    connections.forEach(([start, end]) => {
        const startLm = landmarks[start];
        const endLm = landmarks[end];
        if (startLm && endLm && startLm.visibility > 0.5 && endLm.visibility > 0.5) {
            const startX = startLm.x * canvas.width;
            const startY = startLm.y * canvas.height;
            const endX = endLm.x * canvas.width;
            const endY = endLm.y * canvas.height;
            
            ctx.beginPath();
            ctx.moveTo(startX, startY);
            ctx.lineTo(endX, endY);
            ctx.stroke();
        }
    });

    // Draw points
    ctx.fillStyle = "#10b981";
    landmarks.forEach(lm => {
        // MediaPipe returns normalized coordinates (0-1), map them to canvas
        const x = lm.x * canvas.width;
        const y = lm.y * canvas.height;
        
        // Only draw if visibility is high enough
        if (lm.visibility > 0.5) {
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, 2 * Math.PI);
            ctx.fill();
        }
    });
}

// Chatbot Logic
const chatSendBtn = document.getElementById('chat-send-btn');
const chatInput = document.getElementById('chat-input-field');
const chatMessages = document.getElementById('chat-messages');

async function sendChatMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Add user message to UI
    appendMessage(text, 'user');
    chatInput.value = '';

    // Show typing indicator
    const typingIndicator = appendMessage('Typing...', 'bot');
    typingIndicator.classList.add('typing');

    try {
        const response = await fetch(`${API_BASE_URL}/api/chatbot/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: text })
        });

        // Remove typing indicator
        typingIndicator.remove();

        if (response.ok) {
            const data = await response.json();
            appendMessage(data.reply, 'bot');
        } else {
            appendMessage("Sorry, I'm having trouble connecting to the server.", 'bot');
            showNotification('Chat service unavailable', 'error');
        }
    } catch (err) {
        console.error("Chat error:", err);
        // Remove typing indicator
        typingIndicator.remove();
        appendMessage("Network error. Is the AI server running?", 'bot');
        showNotification('Network error', 'error');
    }
}

function appendMessage(text, sender) {
    const div = document.createElement('div');
    div.classList.add('message', sender);
    const p = document.createElement('p');
    p.innerText = text;
    div.appendChild(p);
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight; // auto-scroll
    return div; // Return the message element for typing indicator
}

chatSendBtn.addEventListener('click', sendChatMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendChatMessage();
    }
});

// Analytics Logic
const refreshAnalyticsBtn = document.getElementById('refresh-analytics');
const ctxChart = document.getElementById('performanceChart');
let perfChart = null;

async function loadAnalytics() {
    const refreshBtn = document.getElementById('refresh-analytics');
    if (refreshBtn) {
        setLoading(refreshBtn, true);
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/analytics/summary?user_id=${CURRENT_USER.id}`);
        if (response.ok) {
            const data = await response.json();

            const user = data.user || CURRENT_USER;
            CURRENT_USER = { ...CURRENT_USER, name: user.name, avatar: user.avatar };
            setUserProfile(user);

            // Update main dashboard stats - with null checks
            const statCalories = document.getElementById('stat-calories');
            if (statCalories) statCalories.innerText = `${data.total_calories} kcal`;
            
            const statHours = document.getElementById('stat-hours');
            if (statHours) statHours.innerText = `${data.hours_trained.toFixed(1)}h`;
            
            const statHeart = document.getElementById('stat-heart-rate');
            if (statHeart) statHeart.innerText = `${data.avg_heart_rate_bpm} bpm`;
            
            const statScore = document.getElementById('stat-score');
            if (statScore) statScore.innerText = `${data.weekly_performance_score}/100`;

            // Update habit prediction
            const habitEl = document.getElementById('habit-prediction');
            if (habitEl) {
                habitEl.innerHTML = data.habit_prediction || habitEl.innerHTML;
            }

            // Update user info
            const userEmail = document.getElementById('user-email');
            if (userEmail) userEmail.innerText = user.email || 'N/A';
            
            const fitnessLevel = document.getElementById('fitness-level');
            if (fitnessLevel) fitnessLevel.innerText = user.fitness_level || 'N/A';
            
            const personalBest = document.getElementById('personal-best');
            if (personalBest) personalBest.innerText = data.personal_best || 'N/A';
            
            const workoutsCount = document.getElementById('workouts-count');
            if (workoutsCount) workoutsCount.innerText = data.workouts_this_week || 0;
            
            const memberSince = document.getElementById('member-since');
            if (memberSince) memberSince.innerText = formatDate(user.joined_date);

            // Update user goals
            const goalsEl = document.getElementById('user-goals');
            if (goalsEl && Array.isArray(user.goals)) {
                goalsEl.innerHTML = '';
                user.goals.forEach(goal => {
                    const li = document.createElement('li');
                    li.style.padding = '0.5rem 0';
                    li.innerHTML = `<i class="fa-solid fa-check" style="color: #10b981; margin-right: 0.5rem;"></i> ${goal}`;
                    goalsEl.appendChild(li);
                });
            }

            // Update recent workouts
            const workoutsEl = document.getElementById('recent-workouts');
            if (workoutsEl && Array.isArray(data.recent_workouts)) {
                workoutsEl.innerHTML = '';
                data.recent_workouts.forEach(workout => {
                    const div = document.createElement('div');
                    div.style.cssText = 'padding: 1rem; background: rgba(15, 23, 42, 0.5); border-radius: 8px; margin-bottom: 0.5rem;';
                    div.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 600;">${workout.exercise}</span>
                            <span style="color: #10b981;">${workout.reps} reps × ${workout.weight}</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 0.5rem;">${formatDate(workout.date)}</div>
                    `;
                    workoutsEl.appendChild(div);
                });
            }

            // Update IoT status list
            const iotStatusList = document.getElementById('iot-status-list');
            if (iotStatusList && Array.isArray(data.iot_status)) {
                iotStatusList.innerHTML = '';
                data.iot_status.forEach(item => {
                    const li = document.createElement('li');
                    const status = document.createElement('span');
                    const statusClass = item.status.toLowerCase().replace(/\s+/g, '-');

                    status.className = `status ${statusClass}`;
                    status.innerText = item.status;
                    li.innerText = `${item.label} `;
                    li.appendChild(status);
                    iotStatusList.appendChild(li);
                });
            }

            // Update chart with heart rate data
            if (ctxChart) {
                const iotData = data.recent_iot_data;
                const labels = iotData.map(d => new Date(d.timestamp * 1000).toLocaleTimeString());
                const heartRates = iotData.map(d => d.heart_rate_bpm);

                if (perfChart) {
                    perfChart.destroy();
                }

                perfChart = new Chart(ctxChart, {
                    type: 'line',
                    data: {
                        labels: labels.length ? labels : ['10:00', '10:05', '10:10', '10:15', '10:20'],
                        datasets: [{
                            label: 'Heart Rate (BPM)',
                            data: heartRates.length ? heartRates : [110, 115, 125, 140, 135],
                            borderColor: '#ef4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: false,
                                grid: { color: 'rgba(255,255,255,0.05)' },
                                ticks: { color: '#94a3b8' }
                            },
                            x: {
                                grid: { color: 'rgba(255,255,255,0.05)' },
                                ticks: { color: '#94a3b8' }
                            }
                        },
                        plugins: {
                            legend: { labels: { color: '#f8fafc' } }
                        }
                    }
                });
            }

            showNotification('Dashboard updated!', 'success');
        } else {
            showNotification('Failed to load dashboard', 'error');
        }
    } catch (err) {
        console.error("Dashboard fetch error", err);
        showNotification('Network error loading dashboard', 'error');
    } finally {
        if (refreshBtn) {
            setLoading(refreshBtn, false);
        }
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: '2-digit', month: 'short', day: 'numeric' });
}

if (refreshAnalyticsBtn) {
    refreshAnalyticsBtn.addEventListener('click', loadAnalytics);
}

// Load analytics when analytics tab is clicked
document.querySelector('[data-target="analytics"]').addEventListener('click', () => {
    setTimeout(loadAnalytics, 100); // slight delay to let view render
});

// Profile Form Handler
const profileForm = document.getElementById('profile-form');
const profileCancelBtn = document.getElementById('profile-cancel-btn');

function populateProfileForm() {
    const profileNameEl = document.getElementById('profile-name');
    if (profileNameEl) {
        profileNameEl.value = CURRENT_USER.name || '';
    }
    const profileFitnessEl = document.getElementById('profile-fitness-level');
    if (profileFitnessEl) {
        profileFitnessEl.value = '';
    }
}

if (profileForm) {
    profileForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const profileNameEl = document.getElementById('profile-name');
        const profileEmailEl = document.getElementById('profile-email');
        const profileAgeEl = document.getElementById('profile-age');
        const profileWeightEl = document.getElementById('profile-weight');
        const profileHeightEl = document.getElementById('profile-height');
        const profileFitnessEl = document.getElementById('profile-fitness-level');
        
        const name = profileNameEl?.value.trim() || '';
        const email = profileEmailEl?.value.trim() || '';
        const age = parseInt(profileAgeEl?.value) || 0;
        const weight = parseFloat(profileWeightEl?.value) || 0;
        const height = parseFloat(profileHeightEl?.value) || 0;
        const fitnessLevel = profileFitnessEl?.value || '';
        
        // Collect selected goals
        const goals = [];
        document.querySelectorAll('input[id^="goal-"]:checked').forEach(checkbox => {
            goals.push(checkbox.value);
        });
        
        // Validation
        if (!name || !email || !age || !weight || !height || !fitnessLevel) {
            showNotification('Please fill in all required fields', 'error');
            return;
        }
        
        if (goals.length === 0) {
            showNotification('Please select at least one fitness goal', 'error');
            return;
        }
        
        const submitBtn = profileForm.querySelector('button[type="submit"]');
        setLoading(submitBtn, true);
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/users/${CURRENT_USER.id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    age: age,
                    weight_kg: weight,
                    height_cm: height,
                    fitness_level: fitnessLevel,
                    goals: goals
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                showNotification('Profile saved successfully!', 'success');
                CURRENT_USER.name = name;
                CURRENT_USER.avatar = `https://ui-avatars.com/api/?name=${name}&background=0D8ABC&color=fff`;
                setUserProfile();
                await loadAnalytics();
            } else {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                showNotification(`Error: ${errorData.detail || 'Failed to save profile'}`, 'error');
            }
        } catch (err) {
            console.error("Profile save error:", err);
            showNotification("Failed to save profile. Make sure the backend is running.", 'error');
        } finally {
            setLoading(submitBtn, false);
        }
    });
}

if (profileCancelBtn) {
    profileCancelBtn.addEventListener('click', () => {
        if (profileForm) {
            profileForm.reset();
        }
        showNotification('Form cleared', 'success', 2000);
    });
}

// Load profile data when profile tab is clicked
const profileTabEl = document.querySelector('[data-target="profile"]');
if (profileTabEl) {
    profileTabEl.addEventListener('click', () => {
        setTimeout(() => {
            fetch(`${API_BASE_URL}/api/users/${CURRENT_USER.id}`)
                .then(res => res.json())
                .then(data => {
                    if (data.name) {
                        const profileNameEl = document.getElementById('profile-name');
                        const profileEmailEl = document.getElementById('profile-email');
                        const profileFitnessEl = document.getElementById('profile-fitness-level');
                        const profileJoinedEl = document.getElementById('profile-joined');
                        
                        if (profileNameEl) profileNameEl.value = data.name || '';
                        if (profileEmailEl) profileEmailEl.value = data.email || '';
                        if (profileFitnessEl) profileFitnessEl.value = data.fitness_level || '';
                        if (profileJoinedEl) profileJoinedEl.innerText = formatDate(data.joined_date || new Date().toISOString());
                        
                        // Clear all goal checkboxes first
                        document.querySelectorAll('input[id^="goal-"]').forEach(cb => cb.checked = false);
                        
                        // Check matching goals
                        if (Array.isArray(data.goals)) {
                            data.goals.forEach(goal => {
                                const checkboxId = 'goal-' + goal.toLowerCase().replace(/\s+/g, '-');
                                const checkbox = document.getElementById(checkboxId);
                                if (checkbox) checkbox.checked = true;
                            });
                        }
                    }
                })
                .catch(err => console.error("Error loading profile:", err));
        }, 100);
    });
}

// Page load animation and initialization
document.addEventListener('DOMContentLoaded', () => {
    // Add fade-in animation to the app container
    const appContainer = document.querySelector('.app-container');
    if (appContainer) {
        appContainer.style.opacity = '0';
        appContainer.style.transform = 'translateY(20px)';
        appContainer.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';

        setTimeout(() => {
            appContainer.style.opacity = '1';
            appContainer.style.transform = 'translateY(0)';
        }, 100);
    }

    setUserProfile();
    loadAnalytics();

    // Show welcome notification
    setTimeout(() => {
        showNotification('Welcome to FitAI! Your personal fitness assistant is ready.', 'success', 4000);
    }, 1000);
});
