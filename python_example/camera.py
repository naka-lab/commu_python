import cv2

def main():
    cap = cv2.VideoCapture("udp://127.0.0.1:12345")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        k = cv2.waitKey(1)
        if k == 27:
            break

        cv2.imshow('image', frame)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()