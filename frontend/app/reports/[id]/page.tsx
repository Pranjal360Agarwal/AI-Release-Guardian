import { ReportView } from "@/components/ReportView";
import { getReport } from "@/lib/api";

export default async function ReportPage({ params }: { params: { id: string } }) {
  const report = await getReport(params.id);
  return <ReportView report={report} />;
}
