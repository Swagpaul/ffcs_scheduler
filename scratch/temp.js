
    const GRID_MAPPING = {
        'MON': {
            'THEORY': ['A1', 'F1', 'D1', 'TB1', 'TG1', '-', '-', 'A2', 'F2', 'D2', 'TB2', 'TG2', '-', 'V3'],
            'LAB': ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', '-', 'L31', 'L32', 'L33', 'L34', 'L35', 'L36', '-']
        },
        'TUE': {
            'THEORY': ['B1', 'G1', 'E1', 'TC1', 'TAA1', '-', '-', 'B2', 'G2', 'E2', 'TC2', 'TAA2', '-', 'V4'],
            'LAB': ['L7', 'L8', 'L9', 'L10', 'L11', 'L12', '-', 'L37', 'L38', 'L39', 'L40', 'L41', 'L42', '-']
        },
        'WED': {
            'THEORY': ['C1', 'A1', 'F1', 'V1', 'V2', '-', '-', 'C2', 'A2', 'F2', 'TD2', 'TBB2', '-', 'V5'],
            'LAB': ['L13', 'L14', 'L15', 'L16', 'L17', 'L18', '-', 'L43', 'L44', 'L45', 'L46', 'L47', 'L48', '-']
        },
        'THU': {
            'THEORY': ['D1', 'B1', 'G1', 'TE1', 'TCC1', '-', '-', 'D2', 'B2', 'G2', 'TE2', 'TCC2', '-', 'V6'],
            'LAB': ['L19', 'L20', 'L21', 'L22', 'L23', 'L24', '-', 'L49', 'L50', 'L51', 'L52', 'L53', 'L54', '-']
        },
        'FRI': {
            'THEORY': ['E1', 'C1', 'TA1', 'TF1', 'TD1', '-', '-', 'E2', 'C2', 'TA2', 'TF2', 'TDD2', '-', 'V7'],
            'LAB': ['L25', 'L26', 'L27', 'L28', 'L29', 'L30', '-', 'L55', 'L56', 'L57', 'L58', 'L59', 'L60', '-']
        },
        'SAT': {
            'THEORY': ['V8', 'X11', 'X12', 'Y11', 'Y12', '-', '-', 'X21', 'Z21', 'Y21', 'W21', 'W22', '-', 'V9'],
            'LAB': ['L71', 'L72', 'L73', 'L74', 'L75', 'L76', '-', 'L77', 'L78', 'L79', 'L80', 'L81', 'L82', '-']
        },
        'SUN': {
            'THEORY': ['V10', 'Y11', 'Y12', 'X11', 'X12', '-', '-', 'Y21', 'Z21', 'X21', 'W21', 'W22', '-', 'V11'],
            'LAB': ['L83', 'L84', 'L85', 'L86', 'L87', 'L88', '-', 'L89', 'L90', 'L91', 'L92', 'L93', 'L94', '-']
        }
    };

    let timetableColors = {};

    function getSubjectColor(name) {
        if (!name) return '#475569';
        return timetableColors[name] || '#475569';
    }

    function assignTimetableColors(data) {
        if (!data || !Array.isArray(data)) return {};
        const uniqueNames = [...new Set(data.map(c => c.course_name).filter(n => n))];
        const colors = {};
        
        if (uniqueNames.length === 0) return {};

        // Use HSL with even spacing for distinctness
        uniqueNames.forEach((name, i) => {
            const hue = (i * (360 / uniqueNames.length) + 20) % 360;
            colors[name] = `hsl(${hue}, 85%, 65%)`;
        });
        
        return colors;
    }

    const THEORY_TIMES = {
        start: ['08:00', '09:00', '10:00', '11:00', '12:00', '-', '-', '14:00', '15:00', '16:00', '17:00', '18:00', '18:51', '19:01'],
        end: ['08:50', '09:50', '10:50', '11:50', '12:50', '-', '-', '14:50', '15:50', '16:50', '17:50', '18:50', '19:00', '19:50']
    };

    const LAB_TIMES = {
        start: ['08:00', '08:51', '09:51', '10:41', '11:40', '12:31', '-', '14:00', '14:51', '15:51', '16:41', '17:40', '18:31', '-'],
        end: ['08:50', '09:40', '10:40', '11:30', '12:30', '13:20', '-', '14:50', '15:40', '16:40', '17:30', '18:30', '19:20', '-']
    };

    async function init() {
        const list = document.getElementById('timetables-list');
        if (!list) {
            console.error("Critical: 'timetables-list' element not found!");
            return;
        }

        console.log("FFCS: Initializing results fetch...");
        try {
            const r = await fetch('/api/timetables');
            if (!r.ok) {
                const errData = await r.json().catch(() => ({}));
                throw new Error(errData.error || `HTTP ${r.status}`);
            }
            const tts = await r.json();
            console.log(`FFCS: Received ${tts.length} timetables`);
            renderTimetables(tts);
            
            // Fetch AI rankings in background
            fetchAIRanking();
        } catch (err) {
            console.error("FFCS Init Error:", err);
            list.innerHTML = `
                <div class="card" style="border-color: var(--danger); color: var(--danger); text-align: center; padding: 3rem;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 1.5rem; display: block;"></i>
                    <h3 style="font-size: 1.5rem; margin-bottom: 1rem;">Failed to load results</h3>
                    <p style="margin-bottom: 2rem; opacity: 0.8;">${err.message}</p>
                    <button class="btn btn-primary" onclick="location.reload()">
                        <i class="fas fa-sync"></i> Retry Connection
                    </button>
                </div>
            `;
        }
    }

    function renderTimetables(tts) {
        const list = document.getElementById('timetables-list');
        try {
            if (!tts || tts.length === 0) {
                list.innerHTML = `
                    <div class="card" style="text-align: center; padding: 4rem; border-style: dashed; border-color: var(--highlight-purple);">
                        <i class="fas fa-calendar-times" style="font-size: 3rem; color: var(--highlight-purple); margin-bottom: 1.5rem; display: block;"></i>
                        <h3 style="font-size: 1.5rem; margin-bottom: 1rem;">No Timetables Found</h3>
                        <p style="color: var(--text-muted); margin-bottom: 2rem;">We haven't generated any schedules for you yet. Add your courses and let the engine work its magic!</p>
                        <a href="/generate" class="btn btn-primary">
                            <i class="fas fa-magic"></i> Generate Now
                        </a>
                    </div>
                `;
                return;
            }

            list.innerHTML = tts.map((tt, idx) => {
                if (!tt || !tt.data) return '';
                
                // Assign unique colors for this specific timetable
                timetableColors = assignTimetableColors(tt.data);
                
                return `
                <div class="card timetable-card animate-fade" style="position: relative; animation-delay: ${idx * 0.1}s;">
                    <div class="score-badge">Score: ${tt.score}</div>
                    <h3 style="margin-bottom: 1.5rem;">Option #${idx + 1}</h3>
                    
                    <div class="table-responsive">
                        <table class="ffcs-table">
                        <thead>
                            <tr class="header-row">
                                <th rowspan="2" colspan="2" style="width: 90px;">THEORY</th>
                                <th style="width: 40px;">Start</th>
                                ${THEORY_TIMES.start.map((t, i) => i === 7 ? '<th rowspan="4" class="lunch-cell">LUNCH</th>' + `<th>${t}</th>` : `<th>${t}</th>`).join('')}
                            </tr>
                            <tr class="header-row">
                                <th>End</th>
                                ${THEORY_TIMES.end.map(t => `<th>${t}</th>`).join('')}
                            </tr>
                            <tr class="header-row">
                                <th rowspan="2" colspan="2">LAB</th>
                                <th>Start</th>
                                ${LAB_TIMES.start.map(t => `<th>${t}</th>`).join('')}
                            </tr>
                            <tr class="header-row">
                                <th>End</th>
                                ${LAB_TIMES.end.map(t => `<th>${t}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            ${Object.keys(GRID_MAPPING).map(day => `
                            <tr>
                                <td rowspan="2" class="day-cell">${day}</td>
                                <td class="type-cell">THEORY</td>
                                <td style="font-size: 0.5rem; color: #444;">-</td>
                                ${GRID_MAPPING[day].THEORY.map((slot, i) => i === 7 ? '<td rowspan="2" class="lunch-cell">LUNCH</td>' + renderSlotCell(tt.data, slot, 'theory') : renderSlotCell(tt.data, slot, 'theory')).join('')}
                            </tr>
                            <tr>
                                <td class="type-cell">LAB</td>
                                <td style="font-size: 0.5rem; color: #444;">-</td>
                                ${GRID_MAPPING[day].LAB.map((slot, i) => i === 7 ? '' : renderSlotCell(tt.data, slot, 'lab')).join('')}
                            </tr>
                        `).join('')}
                        </tbody>
                    </table>
                    </div>
                    
                    <div style="margin-top: 3rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem;">
                        ${(tt.data || []).map(renderCourseCard).join('')}
                    </div>
                </div>
            `;
            }).join('');
        } catch (e) {
            console.error("Rendering failed:", e);
            list.innerHTML = `<div class="card" style="border-color: var(--danger); color: var(--danger);">
                <h3>Rendering Error</h3>
                <p>${e.message}</p>
            </div>`;
        }
    }

    function renderCourseCard(c) {
        const color = getSubjectColor(c.course_name);
        return `
            <div style="font-size: 0.9rem; background: var(--card-bg); padding: 1.5rem; border-radius: var(--radius-md); border: var(--border-width) solid var(--border-color); border-bottom: 8px solid ${color};">
                <div style="font-weight: 800; color: ${color}; margin-bottom: 4px; display: flex; justify-content: space-between; align-items: flex-start;">
                    <span>${c.course_name}</span>
                    <span style="font-size: 0.65rem; background: ${color}22; padding: 2px 6px; border-radius: 4px; border: 1px solid ${color}44;">${c.course_code || 'COURSE'}</span>
                </div>
                <div style="color: var(--text-muted); font-size: 0.75rem; margin-bottom: 8px;">${c.prof_name}</div>
                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                    ${c.theory_slot ? `<span class="badge" style="background: ${color}; color: var(--bg-black); font-size: 0.7rem; font-weight: 900; border: none; padding: 4px 10px; border-radius: 6px;">${c.theory_slot}</span>` : ''}
                    ${c.lab_slot ? `<span class="badge" style="background: ${color}; color: var(--bg-black); font-size: 0.7rem; font-weight: 900; border: none; padding: 4px 10px; border-radius: 6px;">${c.lab_slot}</span>` : ''}
                </div>
            </div>
        `;
    }

    function renderRankingCard(r) {
        return `
            <div style="margin-bottom: 1.5rem;">
                <h4 style="color: var(--primary);">Rank #${r.rank} - Timetable ID: ${r.timetable_id}</h4>
                <p style="font-size: 0.9rem; margin: 0.5rem 0;">${r.explanation}</p>
                <ul style="font-size: 0.8rem; color: var(--accent); list-style: none;">
                    ${r.pros.map(p => `<li><i class="fas fa-check"></i> ${p}</li>`).join('')}
                </ul>
                <ul style="font-size: 0.8rem; color: var(--danger); list-style: none;">
                    ${r.cons.map(c => `<li><i class="fas fa-times"></i> ${c}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    function renderSlotCell(data, slot, type) {
        if (slot === '-') return '<td>-</td>';
        if (!data || !Array.isArray(data)) return '<td></td>';

        const course = data.find(c => {
            const slotsStr = (type === 'theory' ? c.theory_slot : c.lab_slot) || "";
            // Split by + or , and trim
            return slotsStr.toUpperCase().split(/[+,]/).map(s => s.trim()).includes(slot.toUpperCase());
        });

        return `
            <td class="slot-cell">
                <span class="slot-label">${slot}</span>
                ${course ? `
                    <div class="class-filled" style="background-color: ${getSubjectColor(course.course_name)}">
                        <div class="course-code">${slot}-${course.course_name.split(' ')[0]}</div>
                        <div class="course-prof">${course.prof_name.split(' ')[0]}</div>
                    </div>
                ` : ''}
            </td>
        `;
    }

    function fetchAIRanking() {
        const section = document.getElementById('ai-section');
        const content = document.getElementById('ai-content');
        section.style.display = 'block';

        fetch('/api/best')
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    content.innerHTML = `<p style="color: var(--danger)">${data.error}</p>`;
                    return;
                }

                content.innerHTML = `
                    <div class="ai-explanation">
                        <p style="font-weight: 600; font-style: italic; color: var(--text-main);">${data.overall_summary}</p>
                    </div>
                    <div class="grid">
                        ${data.rankings.map(renderRankingCard).join('')}
                    </div>
                `;
            })
            .catch(err => {
                content.innerHTML = `<p style="color: var(--danger)">Connection failed. Please check your settings.</p>`;
            });
    }

    // Run immediately since script is at the end of body
    init().catch(e => console.error("Top-level init error:", e));
