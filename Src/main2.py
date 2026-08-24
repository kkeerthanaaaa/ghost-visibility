import cv2
import time
from engine2 import Ghost, HandTracker


# ============================
# CAMERA
# ============================

# Loading camera frame
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Could not open camera 0. Check camera permissions and whether another app is using it.")

# setting width and height for camera frame
cap.set (cv2.CAP_PROP_FRAME_WIDTH,1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)

# Force a Higher Frame Rate (Request 30 or 60 FPS)
cap.set(cv2.CAP_PROP_FPS, 30)

# Optimize Internal Buffer (Crucial for eliminating movement lag)
# Keeps only the most recent frame in memory instead of building a backlog
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# ===============================
# OBJECTS
# ===============================
ghost = Ghost()
hand_tracker = HandTracker()

# ================================
# PINCH SETTINGS
# ================================

PINCH_THRESHOLD = 0.06

# Prevent repeated triggering while fingers remain together
pinch_active = False


# =========================================================
# FPS
# =========================================================

previous_time = time.time()
fps = 0


# =========================================================
# PINCH MESSAGE
# =========================================================

pinch_message = ""
pinch_message_timer = 0


# =========================================================
# MAIN LOOP
# =========================================================

while True:
    # extracting frame from video
    ret, frame = cap.read()

    # if video not found it will break the loop
    if not ret:
        print("Video Not Found")
        break

    # Flipping the camera
    frame = cv2.flip(frame,1)
    
    # FPS calculation
    current_time = time.time()
    time_difference = current_time - previous_time

    if time_difference > 0:
        fps = 1/ time_difference

    previous_time = current_time

    # Keyboard input for capturing Background
    key = cv2.waitKey(1) & 0xFF

    # Hand Detection
    hand_results = hand_tracker.process(frame)
    pinch_distance = hand_tracker.get_pinch_distance(hand_results)

    # Hand Count
    if hand_results.multi_hand_landmarks:
        hands_count = len(
            hand_results.multi_hand_landmarks
        )

    else:
        hands_count = 0

    # =====================================================
    # PINCH DETECTION
    # =====================================================

    if not ghost.capture_background and ghost.background is not None:

        if pinch_distance is not None:

            # Thumb + middle finger touching
            if pinch_distance < PINCH_THRESHOLD:

                # Trigger ONLY when entering pinch
                if not pinch_active:

                    ghost.toggle_ghost()

                    pinch_active = True

                    pinch_message = "PINCH DETECTED!"

                    pinch_message_timer = time.time()

            else:

                # Fingers separated
                pinch_active = False

        else:

            # No hand detected
            pinch_active = False

    else:

        # Background calculation in progress
        # Completely disable gesture
        pinch_active = False
        
    # capturing background
    ghost.store_background(frame,key)

    # segmentation
    mask = ghost.segmentation(frame, hand_results)

    # Ghost effect
    ghost_frame=ghost.create_ghost(
        frame,
        mask
    )

    # Display Frame
    if ghost_frame is None:
        display = frame.copy()

    else:
        display = ghost_frame.copy()

    
    # =====================================================
    # BACKGROUND STATUS
    # =====================================================

    if ghost.capture_background:

        # ---------------------------------------------
        # CALCULATING BACKGROUND
        # ---------------------------------------------

        progress = int(
            (ghost.background_count /
            ghost.total_background_frames) * 100
        )

        background_text = (
            f"CALCULATING BACKGROUND... {progress}%"
        )

        cv2.putText(
            display,
            background_text,
            (25, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

        # Progress bar
        bar_x = 25
        bar_y = 150

        bar_width = min(
            400,
            display.shape[1] - 50
        )

        bar_height = 12

        filled_width = int(
            bar_width * progress / 100
        )

        # Outer bar
        cv2.rectangle(
            display,
            (bar_x, bar_y),
            (
                bar_x + bar_width,
                bar_y + bar_height
            ),
            (255, 255, 255),
            2
        )

        # Filled portion
        cv2.rectangle(
            display,
            (bar_x, bar_y),
            (
                bar_x + filled_width,
                bar_y + bar_height
            ),
            (255, 255, 255),
            -1
        )


    elif ghost.background is None:

        # ---------------------------------------------
        # WAITING FOR SPACE
        # ---------------------------------------------

        cv2.putText(
            display,
            "PRESS SPACE TO CAPTURE BACKGROUND",
            (25, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

    # =====================================================
    # HUD
    # =====================================================

    h, w = display.shape[:2]

    # =====================================================
    # HUD SIZES
    # =====================================================

    top_bar_height = 80
    bottom_bar_height = 60


    # =====================================================
    # TOP BAR
    # =====================================================

    cv2.rectangle(
        display,
        (0, 0),
        (w, top_bar_height),
        (20, 20, 20),
        -1
    )


    # =====================================================
    # BOTTOM BAR
    # =====================================================

    cv2.rectangle(
        display,
        (0, h - bottom_bar_height),
        (w, h),
        (20, 20, 20),
        -1
    )


    # =====================================================
    # TITLE
    # =====================================================

    cv2.putText(
        display,
        "GHOST / INVISIBILITY MODE",
        (25, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )


    # =====================================================
    # MODE
    # =====================================================

    if ghost.invisible:

        mode_text = "[G] GHOST ACTIVE"

    else:

        mode_text = "[ ] LIVE MODE"


    mode_size = cv2.getTextSize(
        mode_text,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        2
    )[0]


    mode_x = w - mode_size[0] - 20


    cv2.putText(
        display,
        mode_text,
        (mode_x, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )


    # =====================================================
    # FPS
    # =====================================================

    fps_text = f"FPS: {fps:.1f}"

    fps_size = cv2.getTextSize(
        fps_text,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        1
    )[0]


    fps_x = w - fps_size[0] - 20


    cv2.putText(
        display,
        fps_text,
        (fps_x, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1
    )


    # =====================================================
    # GHOST %
    # =====================================================

    ghost_percentage = int(
        ghost.alpha * 100
    )


    cv2.putText(
        display,
        f"GHOST: {ghost_percentage}%",
        (20, h - 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1
    )


    # =====================================================
    # HAND COUNT
    # =====================================================

    hands_text = f"HANDS: {hands_count}"

    cv2.putText(
        display,
        hands_text,
        (180, h - 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1
    )


    # =====================================================
    # GESTURE STATUS
    # =====================================================
    
    if ghost.capture_background:

        gesture_text = "CALCULATING BACKGROUND"

    elif ghost.background is None:

        gesture_text = "BACKGROUND NOT READY"

    elif pinch_distance is None:

        gesture_text = "SHOW HAND"

    elif pinch_distance < PINCH_THRESHOLD:

        gesture_text = "PINCH DETECTED"

    else:

        gesture_text = "PINCH READY"

    cv2.putText(
        display,
        gesture_text,
        (320, h - 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1
    )

    # ===================================
    # PINCH POPUP
    # ===================================

    if pinch_message != "":

        elapsed = (
            time.time()
            - pinch_message_timer
        )

        if elapsed < 1.0:

            # ---------------------------------------------
            # Get actual frame size
            # ---------------------------------------------

            h, w = display.shape[:2]

            # ---------------------------------------------
            # Text size
            # ---------------------------------------------

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            thickness = 2

            text_size = cv2.getTextSize(
                pinch_message,
                font,
                font_scale,
                thickness
            )[0]

            # ---------------------------------------------
            # Center horizontally
            # ---------------------------------------------

            text_x = (
                w - text_size[0]
            ) // 2

            # Keep text inside frame
            text_x = max(
                10,
                text_x
            )

            # ---------------------------------------------
            # Draw popup
            # ---------------------------------------------

            cv2.putText(
                display,
                pinch_message,
                (text_x, 125),
                font,
                font_scale,
                (255, 255, 255),
                thickness
            )

        else:

            pinch_message = ""

    # =====================================================
    # ONE SINGLE WINDOW
    # =====================================================

    cv2.imshow(
        "GHOST",
        display
    )


    # ===========================
    # ESC
    # ===========================

    if key == 27:
        break


# ==========================
# CLEANUP
# ==========================

cap.release()
cv2.destroyAllWindows()