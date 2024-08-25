import threading
from pathlib import Path

import cv2
from ultralytics import YOLO

from app.config import config
from app.models.camera import Camera
from app.models.report import Anomaly, ObjectDetection, Report
from app.models.video_analysis import VideoAnalysis, VideoAnomaly, VideoObjectDetection


class VideoProcessor:
    def __init__(self, source, is_camera: bool = False):
        self.source = source
        self.is_camera = is_camera
        self.bottle_model = YOLO(config.BOTTLE_MODEL_PATH)
        self.fire_model = YOLO(config.FIRE_MODEL_PATH)
        self.object_model = YOLO(config.OBJECT_MODEL_PATH)
        self.fgbg = cv2.createBackgroundSubtractorMOG2()
        self.movement_history = []
        self.area_threshold = 500
        self.movement_threshold = 50

    async def save_report(self, combined_frame, anomalies, is_camera):
        camera = await Camera.get(id=self.source)
        report = Report.get_or_none(camera=camera)
        if report:
            report = await Report.create(
                camera=camera,
                report_type="Video Analysis",
                summary="Anlık kamera analizi",
            )

        for anomaly_data in anomalies:
            anomaly = await Anomaly.create(**anomaly_data)
            await report.anomalies_detected.add(anomaly)

        for object_data in combined_frame:
            obj = await ObjectDetection.create(**object_data)
            await report.objects_detected.add(obj)

        await report.save()

    async def save_video_analysis(
        self, combined_frame, anomalies, video_analysis: VideoAnalysis
    ):
        for anomaly_data in anomalies:
            anomaly = await VideoAnomaly.create(**anomaly_data)
            await video_analysis.anomalies_detected.add(anomaly)

        for object_data in combined_frame:
            obj = await VideoObjectDetection.create(**object_data)
            await video_analysis.objects_detected.add(obj)

        await video_analysis.save()

    def process_frame(self, frame):
        fgmask = self.fgbg.apply(frame)
        contours, _ = cv2.findContours(
            fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        current_movement = []
        for contour in contours:
            if cv2.contourArea(contour) > self.area_threshold:
                x, y, w, h = cv2.boundingRect(contour)
                current_movement.append((x, y, w, h))
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        self.movement_history.append(current_movement)
        anomalies = self.detect_anomalies(current_movement)

        bottle_frame = self.detect_objects(frame, self.bottle_model, ["bottle"])
        fire_frame = self.detect_objects(frame, self.fire_model, ["fire"])
        object_frame = self.detect_objects(
            frame,
            self.object_model,
            [
                "cars-bikes-people",
                "Bus",
                "Bushes",
                "Person",
                "Truck",
                "backpack",
                "bench",
                "bicycle",
                "boat",
                "branch",
                "car",
                "chair",
                "clock",
                "crosswalk",
                "door",
                "elevator",
                "fire_hydrant",
                "green_light",
                "gun",
                "handbag",
                "motorcycle",
                "person",
                "pothole",
                "rat",
                "red_light",
                "scooter",
                "sheep",
                "stairs",
                "stop_sign",
                "suitcase",
                "traffic light",
                "traffic_cone",
                "train",
                "tree",
                "truck",
                "umbrella",
                "yellow_light",
            ],
        )

        combined_frame = cv2.hconcat([fire_frame, bottle_frame, object_frame])
        return combined_frame, anomalies

    def detect_objects(self, frame, model, classnames):
        results = model(frame)
        frame_copy = frame.copy()
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            scores = result.boxes.conf.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy()
            for box, score, cls in zip(boxes, scores, class_ids):
                x1, y1, x2, y2 = map(int, box)
                label = (
                    classnames[int(cls)] if int(cls) < len(classnames) else "Unknown"
                )
                frame_copy = cv2.rectangle(
                    frame_copy, (x1, y1), (x2, y2), (0, 255, 0), 2
                )
                frame_copy = cv2.putText(
                    frame_copy,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 0),
                    2,
                )
        return frame_copy

    def detect_anomalies(self, current_movement):
        anomalies = []
        anomaly_scores = []

        if len(self.movement_history) > 3:
            prev_movement = self.movement_history[-2]
            for x, y, w, h in current_movement:
                for px, py, pw, ph in prev_movement:
                    x_diff = abs(x - px)
                    y_diff = abs(y - py)

                    if (
                        x_diff > self.movement_threshold
                        or y_diff > self.movement_threshold
                    ):
                        anomalies.append((x, y, w, h))
                        anomaly_score = (x_diff + y_diff) / 2
                        anomaly_scores.append(anomaly_score)
                        break

        return anomalies, anomaly_scores

    def run_camera(self):
        cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            combined_frame, anomalies = self.process_frame(frame)
            cv2.imshow("YOLO Models Comparison", combined_frame)
            threading.Thread(
                target=self.save_report, args=(combined_frame, anomalies)
            ).start()

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

    def run_video(self):
        video_analysis = VideoAnalysis.get(id=self.source)
        video_path = Path(video_analysis.file_path, video_analysis.file_name)
        cap = cv2.VideoCapture(video_path)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            combined_frame, anomalies = self.process_frame(frame)
            cv2.imshow("YOLO Models Comparison", combined_frame)
            threading.Thread(
                target=self.save_video_analysis, args=(combined_frame, anomalies)
            ).start()

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()
