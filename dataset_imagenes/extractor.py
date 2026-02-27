import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class ExtractorDeImagenes(Node):
    def __init__(self):
        super().__init__('extractor_imagenes')
        # Nos suscribimos al topic de la cámara
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.guardar_imagen,
            10)
        self.bridge = CvBridge()
        self.contador = 0

    def guardar_imagen(self, msg):
        # Convertir de ROS a OpenCV
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        # Guardar en el disco
        nombre_archivo = f'fotograma_{self.contador:04d}.jpg'
        cv2.imwrite(nombre_archivo, cv_image)
        self.get_logger().info(f'Guardada: {nombre_archivo}')
        self.contador += 1

def main(args=None):
    rclpy.init(args=args)
    nodo = ExtractorDeImagenes()
    print("Escuchando imágenes... ¡Reproduce tu ROS Bag ahora!")
    rclpy.spin(nodo)
    nodo.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
