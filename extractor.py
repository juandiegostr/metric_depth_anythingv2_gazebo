import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os

class ExtractorDeImagenes(Node):
    def __init__(self):
        super().__init__('extractor_imagenes')
        
        # Crear directorios si no existen
        os.makedirs('dataset_imagenes', exist_ok=True)
        os.makedirs('dataset_depth', exist_ok=True)
        
        # Nos suscribimos al topic de la cámara RGB
        self.su_rgb = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.guardar_imagen_rgb,
            10)
            
        # Nos suscribimos al topic de la cámara de profundidad
        self.su_depth = self.create_subscription(
            Image,
            '/camera/depth/image_raw',
            self.guardar_imagen_depth,
            10)

        self.bridge = CvBridge()
        self.contador_rgb = 0
        self.contador_depth = 0

    def guardar_imagen_rgb(self, msg):
        # Convertir de ROS a OpenCV
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        # Guardar en el disco
        nombre_archivo = f'dataset_imagenes/fotograma_{self.contador_rgb:04d}.jpg'
        cv2.imwrite(nombre_archivo, cv_image)
        self.get_logger().info(f'Guardada RGB: {nombre_archivo}')
        self.contador_rgb += 1

    def guardar_imagen_depth(self, msg):
        # Convertir de ROS a OpenCV (generalmente la profundidad llega en 32FC1 o 16UC1)
        import numpy as np
        # Usamos passthrough para que OpenCV obtenga la imagen en el formato original
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='32FC1')
        
        # En Gazebo / ROS, los valores faltantes (infinito) o el fondo a veces generan
        # problemas. Reemplazamos los inf y NaN por 0.0 o un valor manejable.
        cv_image = np.nan_to_num(cv_image, posinf=0.0, neginf=0.0)
        
        # Convertir a 16-bits para poder verlo bien o usarlo en redes. (milímetros)
        # Asumiendo que viene en metros (float32). Lo multiplicamos por 1000.
        cv_image_16 = (cv_image * 1000.0).astype(np.uint16)

        nombre_archivo = f'dataset_depth/profundidad_{self.contador_depth:04d}.tiff'
        cv2.imwrite(nombre_archivo, cv_image_16)
        self.get_logger().info(f'Guardada Depth: {nombre_archivo}')
        self.contador_depth += 1

def main(args=None):
    rclpy.init(args=args)
    nodo = ExtractorDeImagenes()
    print("Escuchando imágenes...")
    rclpy.spin(nodo)
    nodo.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
