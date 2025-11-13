from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import logging

from .services.summary_generator import DashboardSummaryService
from .serializers import DashboardSummarySerializer

logger = logging.getLogger(__name__)


class DashboardSummaryView(APIView):
    """대시보드 요약 데이터 조회 API"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        대시보드 요약 데이터 반환

        Returns:
            HTTP 200 OK: 대시보드 데이터
            HTTP 401 Unauthorized: 인증 실패
            HTTP 500 Internal Server Error: 서버 오류
        """
        try:
            service = DashboardSummaryService()
            summary_data = service.generate_dashboard_summary()

            serializer = DashboardSummarySerializer(data=summary_data)
            serializer.is_valid(raise_exception=True)

            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Dashboard summary generation failed: {str(e)}", exc_info=True)

            return Response(
                {'error': '데이터를 불러오는 중 오류가 발생했습니다.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
