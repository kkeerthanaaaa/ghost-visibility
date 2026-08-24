import cv2
import mediapipe as mp
import numpy as np

class Ghost:
    def __init__(self):
        self.background = None
        self.previous_mask = None

        # Ghost state
        self.invisible = False
        self.alpha = 0.0

        # Background capture settings
        self.background_frames = []
        self.capture_background = False
        self.background_count = 0
        self.total_background_frames = 90
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.segmenter = self.mp_selfie_segmentation.SelfieSegmentation(model_selection=1)
        

    def store_background(self,frame,key):
        
        # Space to capture background
        if key == ord(" "):
            if not self.capture_background:
                self.background_frames = []
                self.background_count = 0
                self.capture_background = True
               

        # Capture multiple frames
        if self.capture_background:

            self.background_frames.append(
                frame.copy()
            )

            self.background_count += 1

            # Enough frames captured
            if self.background_count >= self.total_background_frames:

                # Convert list → NumPy array
                frames = np.array(
                    self.background_frames,
                    dtype=np.float32
                )

                # Average all frames
                self.background = np.mean(
                    frames,
                    axis=0
                ).astype(np.uint8)


                # Save background
                cv2.imwrite(
                    "background.jpg",
                    self.background
                )


                # Reset capture state
                self.background_frames = []
                self.capture_background = False
                self.background_count = 0




    def segmentation(self, frame, hand_results=None):
        h, w = frame.shape[:2]
        # Resize the frame
        small = cv2.resize(
            frame,
            (320,180),
            interpolation=cv2.INTER_AREA
        )

        # BGR → RGB
        rgb_frame = cv2.cvtColor(
            small,
            cv2.COLOR_BGR2RGB
        )

        # MediaPipe segmentation
        result = self.segmenter.process(rgb_frame)

        if result.segmentation_mask is None:

            if self.previous_mask is not None:
                return self.previous_mask

            return np.zeros(
                (h,w),
                dtype=np.float32
            )

        # Resize mask back to original
        mask = cv2.resize(
            result.segmentation_mask,
            (w,h),
            interpolation=cv2.INTER_LINEAR
        ).astype(np.float32)

        # Temporal Smoothing Before threshold
        if self.previous_mask is not None:

            mask = (
                0.6 * mask
                +
                0.4 * self.previous_mask
            )
            
        # Lower threshold
        _, hard = cv2.threshold(
            mask,
            0.25,
            1.0,
            cv2.THRESH_BINARY
        )

        # convert 0-1 to 0-255
        hard8 = (
            hard * 255
        ).astype(np.uint8)

        # creating kernel
        kernel = np.ones(
            (9,9),
            np.uint8
        )
        # fill holes and connect small gaps
        hard8 = cv2.morphologyEx(
            hard8,
            cv2.MORPH_CLOSE,
            kernel
        )
        # Expand the person mask
        hard8 = cv2.dilate(
            hard8,
            kernel,
            iterations=1
        )
        # Back to 0-1
        hard = (
            hard8.astype(np.float32) / 255.0
        )
        # Smooth the expanded mask
        mask = cv2.GaussianBlur(
            hard,
            (3,3),
            0
        )
        # Increase mask strength
        mask = np.clip(
            mask * 0.9,
            0,
            1
        ).astype(np.float32)

        # =====================================================
        # ADD HAND TO PERSON MASK
        # =====================================================

        if hand_results is not None:

            if hand_results.multi_hand_landmarks:

                hand_mask = np.zeros(
                    (h, w),
                    dtype=np.uint8
                )

                for hand_landmarks in hand_results.multi_hand_landmarks:

                    points = []

                    for landmark in hand_landmarks.landmark:

                        x = int(landmark.x * w)
                        y = int(landmark.y * h)

                        # Keep coordinates inside frame
                        x = max(0, min(x, w - 1))
                        y = max(0, min(y, h - 1))

                        points.append(
                            (x, y)
                        )

                    # Create convex hull around hand
                    points = np.array(
                        points,
                        dtype=np.int32
                    )

                    hull = cv2.convexHull(points)

                    cv2.fillConvexPoly(
                        hand_mask,
                        hull,
                        255
                    )

                # Slightly expand the hand area
                hand_kernel = np.ones(
                    (15, 15),
                    np.uint8
                )

                hand_mask = cv2.dilate(
                    hand_mask,
                    hand_kernel,
                    iterations=2
                )

                # Convert to 0-1
                hand_mask = (
                    hand_mask.astype(np.float32) / 255.0
                )

                # Merge hand with person mask
                mask = np.maximum(
                    mask,
                    hand_mask
                )


        # ==========================================
        # DISPLAY MASK
        # ==========================================

        mask_display = (
            mask * 255
        ).astype(np.uint8)

        #cv2.imshow(
        #    "Person Mask",
        #    mask_display
        #)


        # ==========================================
        # DETECTED PERSON
        # ==========================================

        person = cv2.bitwise_and(
            frame,
            frame,
            mask=mask_display
        )

        #cv2.imshow(
        #    "Detected Person",
        #    person
        #)

        # Return soft mask
        return mask

    def create_ghost(self, frame, soft_mask):

        # ==========================================
        # CHECK BACKGROUND
        # ==========================================

        if self.background is None:
            return


        # ==========================================
        # UPDATE GHOST ALPHA
        # ==========================================

        self.update_alpha()


        # ==========================================
        # BACKGROUND
        # ==========================================

        background = self.background

        if background.shape[:2] != frame.shape[:2]:

            background = cv2.resize(
                background,
                (
                    frame.shape[1],
                    frame.shape[0]
                )
            )

        # ==========================================
        # BACKGROUND EXPOSURE MATCHING
        # ==========================================

        background = self.match_background(
            frame,
            background,
            soft_mask
        )

        if self.alpha >= 0.97:
            effective_mask = np.minimum(
                soft_mask * 2.0,
                1
            )

        else:
            effective_mask = soft_mask
        
        # ==========================================
        # ALPHA MASK
        # ==========================================

        final_alpha = (
            effective_mask * self.alpha
        )

        final_alpha = (
            final_alpha[:, :, np.newaxis]
        )


        # ==========================================
        # COMPOSITE
        # ==========================================

        ghost = (
            frame.astype(np.float32)
            *
            (1.0 - final_alpha)
            +
            background.astype(np.float32)
            *
            final_alpha
        )


        # ==========================================
        # CONVERT TO UINT8
        # ==========================================

        ghost = np.clip(
            ghost,
            0,
            255
        ).astype(np.uint8)

        # Return ghost frame
        return ghost

    def toggle_ghost(self):
        self.invisible = not self.invisible

        print(
            "Ghost Mode:",
            "ON" if self.invisible else "OFF"
        )

    def update_alpha(self):
        target = 1.0 if self.invisible else 0.0
        speed = 0.10

        if self.alpha < target:
            self.alpha = min(
                target,
                self.alpha + speed
            )

        elif self.alpha > target:
            self.alpha = max(
                target,
                self.alpha - speed
            )

    def match_background(self, frame, background, soft_mask):

        # Pixels that definitely belong to the background
        bg_area = soft_mask < 0.05

        if np.sum(bg_area) < 1000:
            return background

        # Current live background pixels
        current_pixels = frame[bg_area].astype(np.float32)

        # Stored background pixels
        stored_pixels = background[bg_area].astype(np.float32)

        # Calculate average difference
        difference = (
            np.mean(current_pixels, axis=0)
            -
            np.mean(stored_pixels, axis=0)
        )

        # Apply correction
        corrected = (
            background.astype(np.float32)
            +
            difference
        )

        corrected = np.clip(
            corrected,
            0,
            255
        ).astype(np.uint8)

        return corrected

    
class HandTracker:

    def __init__(self):

        # MediaPipe Hands
        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(
            static_image_mode = False,
            max_num_hands = 1,
            min_detection_confidence = 0.5,
            min_tracking_confidence = 0.5
        )

    def process(self,frame):
        # converting BGR ---> RGB
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # Detect Hand
        results = self.hands.process(
            rgb_frame
        )

        return results

    def get_pinch_distance(self,results):

        # No hand detected
        if not results.multi_hand_landmarks:
            return None

        # Get first hand
        hand = results.multi_hand_landmarks[0]

        # Thumb tip = Landmark 4
        thumb_tip = hand.landmark[4]

        # Middle finger tip = Landmark 12
        middle_tip = hand.landmark[12]

        # Calculate distance
        distance = (
            (thumb_tip.x - middle_tip.x) ** 2
            +
            (thumb_tip.y - middle_tip.y) ** 2
        )**0.5

        return distance