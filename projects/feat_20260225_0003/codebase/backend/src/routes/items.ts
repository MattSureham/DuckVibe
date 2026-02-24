import { Router } from 'express';
import { ItemsController } from '../controllers/items';
import { authMiddleware } from '../middleware/auth';

const router = Router();

router.use(authMiddleware);

router.get('/', ItemsController.list);
router.post('/', ItemsController.create);
router.get('/:id', ItemsController.get);
router.put('/:id', ItemsController.update);
router.delete('/:id', ItemsController.delete);

export { router as itemRoutes };
