from typing import Generic, TypeVar, Type, List, Optional
from django.db import models


T = TypeVar('T', bound=models.Model)


class BaseRepository(Generic[T]):
    """모든 Repository의 기본 클래스"""

    def __init__(self, model_class: Type[T]):
        self.model_class = model_class

    def get_by_id(self, id: int) -> Optional[T]:
        """ID로 단일 객체 조회"""
        try:
            return self.model_class.objects.get(pk=id)
        except self.model_class.DoesNotExist:
            return None

    def get_all(self) -> List[T]:
        """모든 객체 조회"""
        return list(self.model_class.objects.all())

    def filter(self, **kwargs) -> List[T]:
        """조건에 맞는 객체 조회"""
        return list(self.model_class.objects.filter(**kwargs))

    def create(self, **kwargs) -> T:
        """객체 생성"""
        return self.model_class.objects.create(**kwargs)

    def bulk_create(self, objects: List[T]) -> List[T]:
        """대량 객체 생성"""
        return self.model_class.objects.bulk_create(objects)

    def update(self, instance: T, **kwargs) -> T:
        """객체 업데이트"""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def delete(self, instance: T) -> None:
        """객체 삭제"""
        instance.delete()

    def delete_all(self) -> None:
        """모든 객체 삭제"""
        self.model_class.objects.all().delete()

    def count(self) -> int:
        """총 객체 수"""
        return self.model_class.objects.count()

    def exists(self, **kwargs) -> bool:
        """조건에 맞는 객체 존재 여부"""
        return self.model_class.objects.filter(**kwargs).exists()
