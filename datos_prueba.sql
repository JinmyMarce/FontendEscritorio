-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS bdfresaterra;
USE bdfresaterra;

-- Insertar roles
INSERT INTO roles (nombre, descripcion, fecha_creacion) VALUES
('admin', 'Administrador del sistema', NOW()),
('cliente', 'Cliente regular', NOW()),
('vendedor', 'Vendedor de la tienda', NOW());

-- Insertar categorías
INSERT INTO categorias (nombre, descripcion, fecha_creacion) VALUES
('Frutas', 'Frutas frescas y de temporada', NOW()),
('Verduras', 'Verduras frescas y orgánicas', NOW()),
('Lácteos', 'Productos lácteos y derivados', NOW()),
('Carnes', 'Carnes y embutidos', NOW()),
('Bebidas', 'Bebidas y jugos naturales', NOW());

-- Insertar usuarios de prueba
INSERT INTO usuarios (nombre, apellidos, email, password, telefono, fecha_creacion, estado, roles_id_rol) VALUES
-- Administradores
('Admin', 'Principal', 'admin@fresaterra.com', 'admin123', '555-0001', NOW(), 1, 1),
('Juan', 'Administrador', 'juan.admin@fresaterra.com', 'admin123', '555-0002', NOW(), 1, 1),

-- Vendedores
('María', 'Vendedora', 'maria@fresaterra.com', 'vendedor123', '555-0003', NOW(), 1, 3),
('Carlos', 'Vendedor', 'carlos@fresaterra.com', 'vendedor123', '555-0004', NOW(), 1, 3),

-- Clientes
('Ana', 'García', 'ana@email.com', 'cliente123', '555-0101', NOW(), 1, 2),
('Roberto', 'Martínez', 'roberto@email.com', 'cliente123', '555-0102', NOW(), 1, 2),
('Laura', 'Sánchez', 'laura@email.com', 'cliente123', '555-0103', NOW(), 1, 2),
('Pedro', 'López', 'pedro@email.com', 'cliente123', '555-0104', NOW(), 0, 2),
('Carmen', 'Rodríguez', 'carmen@email.com', 'cliente123', '555-0105', NOW(), 0, 2);

-- Insertar productos
INSERT INTO productos (nombre, descripcion, precio, url_imagen, estado, peso, fecha_creacion, categorias_id_categoria) VALUES
-- Frutas
('Manzanas Rojas', 'Manzanas frescas y jugosas', 2.99, 'manzanas.jpg', 'disponible', '1kg', NOW(), 1),
('Plátanos', 'Plátanos maduros y dulces', 1.99, 'platanos.jpg', 'disponible', '1kg', NOW(), 1),
('Naranjas', 'Naranjas jugosas y frescas', 3.49, 'naranjas.jpg', 'disponible', '1kg', NOW(), 1),

-- Verduras
('Lechuga', 'Lechuga fresca y crujiente', 1.49, 'lechuga.jpg', 'disponible', '500g', NOW(), 2),
('Tomates', 'Tomates maduros y frescos', 2.49, 'tomates.jpg', 'disponible', '1kg', NOW(), 2),
('Zanahorias', 'Zanahorias frescas y orgánicas', 1.99, 'zanahorias.jpg', 'disponible', '1kg', NOW(), 2),

-- Lácteos
('Leche Entera', 'Leche fresca de vaca', 2.99, 'leche.jpg', 'disponible', '1L', NOW(), 3),
('Queso Manchego', 'Queso manchego curado', 4.99, 'queso.jpg', 'disponible', '250g', NOW(), 3),
('Yogur Natural', 'Yogur natural sin azúcar', 1.49, 'yogur.jpg', 'disponible', '500g', NOW(), 3);

-- Insertar inventario
INSERT INTO inventarios (cantidad_disponible, fecha_ingreso, ultima_actualizacion, estado, productos_id_producto) VALUES
(100, NOW(), NOW(), 'activo', 1),
(150, NOW(), NOW(), 'activo', 2),
(80, NOW(), NOW(), 'activo', 3),
(50, NOW(), NOW(), 'activo', 4),
(70, NOW(), NOW(), 'activo', 5),
(60, NOW(), NOW(), 'activo', 6),
(200, NOW(), NOW(), 'activo', 7),
(40, NOW(), NOW(), 'activo', 8),
(120, NOW(), NOW(), 'activo', 9);

-- Insertar métodos de pago
INSERT INTO metodos_pago (nombre, activo, fecha_creacion) VALUES
('Efectivo', 1, NOW()),
('Tarjeta de Crédito', 1, NOW()),
('Tarjeta de Débito', 1, NOW()),
('Transferencia Bancaria', 1, NOW());

-- Insertar transportistas
INSERT INTO transportistas (nombre, telefono, tipo_transporte, empresa, placa_vehiculo) VALUES
('Juan Transportes', '555-0201', 'Camioneta', 'Transportes Rápidos', 'ABC-123'),
('María Envíos', '555-0202', 'Furgoneta', 'Envíos Express', 'DEF-456'),
('Carlos Delivery', '555-0203', 'Motocicleta', 'Delivery Rápido', 'GHI-789');

-- Insertar algunos pedidos de ejemplo
INSERT INTO pedidos (monto_total, estado, fecha_creacion, usuarios_id_usuario) VALUES
(25.95, 'completado', DATE_SUB(NOW(), INTERVAL 5 DAY), 5),
(15.47, 'en_proceso', DATE_SUB(NOW(), INTERVAL 3 DAY), 6),
(32.96, 'pendiente', DATE_SUB(NOW(), INTERVAL 1 DAY), 7);

-- Insertar items de pedidos
INSERT INTO pedido_items (cantidad, precio, subtotal, pedidos_id_pedido, productos_id_producto) VALUES
(2, 2.99, 5.98, 1, 1),
(3, 1.99, 5.97, 1, 2),
(4, 3.49, 13.96, 1, 3),
(2, 1.49, 2.98, 2, 4),
(5, 2.49, 12.45, 2, 5),
(3, 4.99, 14.97, 3, 8),
(2, 1.49, 2.98, 3, 9);

-- Insertar envíos
INSERT INTO envios (monto_envio, estado, fecha_envio, transportistas_id_transportista, pedidos_id_pedido) VALUES
(5.00, 'entregado', DATE_SUB(NOW(), INTERVAL 4 DAY), 1, 1),
(5.00, 'en_transito', DATE_SUB(NOW(), INTERVAL 2 DAY), 2, 2),
(5.00, 'pendiente', NOW(), 3, 3);

-- Insertar pagos
INSERT INTO pagos (fecha_pago, monto_pago, estado_pago, referencia_pago, pedidos_id_pedido, metodos_pago_id_metodo_pago) VALUES
(NOW(), 30.95, 'completado', 'PAGO-001', 1, 2),
(NOW(), 20.47, 'pendiente', 'PAGO-002', 2, 1),
(NOW(), 37.96, 'pendiente', 'PAGO-003', 3, 3);

-- Insertar direcciones
INSERT INTO direcciones (calle, numero, distrito, ciudad, referencia, usuarios_id_usuario, predeterminada) VALUES
('Av. Principal', '123', 'Centro', 'Lima', 'Frente al parque', 5, 'si'),
('Jr. Los Olivos', '456', 'San Isidro', 'Lima', 'Esquina con Av. Arequipa', 6, 'si'),
('Calle Los Pinos', '789', 'Miraflores', 'Lima', 'Cerca al mar', 7, 'si');

-- Insertar comentarios
INSERT INTO comentarios (calificacion, contenido, fecha_creacion, usuarios_id_usuario) VALUES
(5, 'Excelente servicio y productos frescos', NOW(), 5),
(4, 'Buen servicio, pero un poco lento', NOW(), 6),
(5, 'Los mejores productos de la zona', NOW(), 7);

-- Insertar mensajes
INSERT INTO mensajes (tipo, contenido) VALUES
('bienvenida', '¡Bienvenido a Fresaterra! Gracias por registrarte.'),
('pedido', 'Tu pedido ha sido recibido y está siendo procesado.'),
('envio', 'Tu pedido está en camino.'),
('entrega', 'Tu pedido ha sido entregado.');

-- Insertar notificaciones
INSERT INTO notificaciones (estado, fecha_creacion, usuarios_id_usuario, mensajes_id_mensaje) VALUES
('no_leida', NOW(), 5, 1),
('leida', NOW(), 6, 2),
('no_leida', NOW(), 7, 3); 