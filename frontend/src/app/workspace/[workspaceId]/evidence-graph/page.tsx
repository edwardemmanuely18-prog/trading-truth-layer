"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  useParams,
} from "next/navigation";

import Navbar from "../../../../components/Navbar";

import InvestigationCanvas from "../../../../components/evidence-graph/InvestigationCanvas";

import InspectorPanel
    from "../../../../components/evidence-graph/InspectorPanel";

import {
    getEvidenceGraph,
    getEvidenceAnalytics,
    EvidenceAnalyticsResponse,
    getCriticalPath,
    getRiskGraph,
    getFullGraph,
} from "../../../../lib/api";

import type {
    EvidenceGraphResponse,
    EvidenceGraphNode,
    EvidenceGraphEdge,
} from "@/lib/evidence-graph/types";

export default function EvidenceGraphPage() {

  const params = useParams();

  const workspaceId = Number(
    params.workspaceId
  );

  const [loading, setLoading] =
    useState(true);

  const [workspaceGraph, setWorkspaceGraph] =
    useState<EvidenceGraphResponse | null>(null);

  const [graph, setGraph] =
    useState<EvidenceGraphResponse | null>(null);

  const [
    analytics,
    setAnalytics
  ] =
  useState<EvidenceAnalyticsResponse | null>(
    null
  );

  const [visibleNodes, setVisibleNodes] =
    useState(20);

  const [visibleEdges, setVisibleEdges] =
    useState(20);

  const [searchTerm, setSearchTerm] =
    useState("");

  const [selectedType, setSelectedType] =
    useState("ALL");

  const [selectedNode, setSelectedNode] =
    useState<EvidenceGraphNode | null>(
      null
    );

  const [selectedClaim, setSelectedClaim] =
    useState<EvidenceGraphNode | null>(
      null
    );

  const [graphPath, setGraphPath] =
    useState<any[]>([]);

  const [graphMode, setGraphMode] =
    useState("FULL INVESTIGATION");

  const [graphStatus, setGraphStatus] =
    useState("Ready");

  useEffect(() => {

    async function load() {

      try {

        const response =
            await getEvidenceGraph(
                workspaceId
            );

        const workspace =
            response as EvidenceGraphResponse;

        setWorkspaceGraph(workspace);

        setGraph(workspace);

        setGraphMode(
            "WORKSPACE GRAPH"
        );

        setGraphStatus(
            "Workspace evidence graph loaded."
        );

        const analytics =
          await getEvidenceAnalytics(
            workspaceId
          );

        setAnalytics(
          analytics
        );

      } catch (err) {

        console.error(err);

      } finally {

        setLoading(false);

      }

    }

    if (!Number.isNaN(workspaceId)) {
      load();
    }

  }, [workspaceId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navbar />

        <div className="mx-auto max-w-7xl px-6 py-10">
          Loading evidence intelligence...
        </div>
      </div>
    );
  }

  if (!graph) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navbar />

        <div className="mx-auto max-w-7xl px-6 py-10">
          Unable to load evidence graph.
        </div>
      </div>
    );
  }

  const claims =
    graph.nodes.filter(
      n => n.type === "CLAIM"
    ).length;

  const reviews =
    graph.nodes.filter(
      n => n.type === "REVIEW"
    ).length;

  const disputes =
    graph.nodes.filter(
      n => n.type === "DISPUTE"
    ).length;

  const alerts =
    graph.nodes.filter(
      n => n.type === "INTEGRITY_ALERT"
    ).length;

  const scans =
    graph.nodes.filter(
      n => n.type === "INTEGRITY_SCAN"
    ).length;

  const batches =
    graph.nodes.filter(
      n => n.type === "IMPORT_BATCH"
    ).length;

  const filteredNodes =
    graph.nodes.filter(node => {

      const matchesSearch =
        node.label
          ?.toLowerCase()
          .includes(
            searchTerm.toLowerCase()
          ) ||
        node.id
          ?.toLowerCase()
          .includes(
            searchTerm.toLowerCase()
          );

      const matchesType =
        selectedType === "ALL"
          ? true
          : node.type === selectedType;

    return (
      matchesSearch &&
      matchesType
    );

  });

  const selectedNodeEdges =
    selectedNode
      ? graph.edges.filter(
          edge =>
            edge.source ===
              selectedNode.id ||
            edge.target ===
              selectedNode.id
        )
      : [];

  const focusedNodeIds =
    new Set<string>();

  if (selectedClaim) {

    const queue = [
      selectedClaim.id
    ];

    while (
      queue.length > 0
    ) {

      const current =
        queue.shift();

      if (
        !current ||
        focusedNodeIds.has(
          current
        )
      ) {
        continue;
      }

      focusedNodeIds.add(
        current
      );

      graph.edges.forEach(
        edge => {

          if (
            edge.source === current
          ) {

            queue.push(
              edge.target
            );

          }

          if (
            edge.target === current
          ) {

            queue.push(
              edge.source
            );

          }

        }
      );

    }

  }

  const focusedNodes =
    graph.nodes.filter(
      node =>
        focusedNodeIds.has(
          node.id
        )
    );

  const upstreamEdges =
    selectedNode
      ? graph.edges.filter(
          edge =>
            edge.target ===
            selectedNode.id
        )
      : [];

  const downstreamEdges =
    selectedNode
      ? graph.edges.filter(
          edge =>
            edge.source ===
            selectedNode.id
        )
      : [];

  const graphDensity =
    graph.node_count > 0
      ? (
          graph.edge_count /
          graph.node_count
        ).toFixed(3)
      : "0";

  const relationshipTypes =
    new Set(
      graph.edges.map(
        edge =>
          edge.relationship
      )
    ).size;

  function traceNodePath(
    nodeId: string
  ) {

    const visited =
      new Set<string>();

    const path: any[] = [];

    function walk(
      current: string
    ) {

      if (
        visited.has(
          current
        )
      ) {
        return;
      }

      visited.add(
        current
      );

      const outgoing =
        graph?.edges.filter(
          edge =>
            edge.source ===
            current
        ) || [];

      outgoing.forEach(
        edge => {

          path.push(edge);

          walk(
            edge.target
          );

        }
      );
    }

    walk(nodeId);

    setGraphPath(path);
  }

  return (
    <div className="min-h-screen bg-slate-50">

      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-10">

        <div className="mb-10">

          <div className="text-xs uppercase tracking-[0.2em] text-slate-500">
            EVIDENCE INTELLIGENCE NETWORK
          </div>

          <h1 className="mt-2 text-5xl font-bold">
            Evidence Graph
          </h1>

          <p className="mt-4 max-w-4xl text-slate-600">
            Institutional relationship
            intelligence connecting
            claims, reviews, disputes,
            integrity events, imports,
            broker infrastructure and
            governance records.
          </p>

        </div>

        <div className="grid gap-4 md:grid-cols-6 mb-8">

          <MetricCard
            title="Claims"
            value={claims}
          />

          <MetricCard
            title="Reviews"
            value={reviews}
          />

          <MetricCard
            title="Disputes"
            value={disputes}
          />

          <MetricCard
            title="Integrity Alerts"
            value={alerts}
          />

          <MetricCard
            title="Integrity Scans"
            value={scans}
          />

          <MetricCard
            title="Import Batches"
            value={batches}
          />

        </div>

        <div className="grid gap-4 md:grid-cols-5 mb-8">

          <MetricCard
            title="Total Nodes"
            value={graph.node_count}
          />

          <MetricCard
            title="Total Edges"
            value={graph.edge_count}
          />

          <MetricCard
            title="Relationships"
            value={graph.edges.length}
          />

          <MetricCard
            title="Graph Density"
            value={graphDensity}
          />

          <MetricCard
            title="Relationship Types"
            value={relationshipTypes}
          />

        </div>

        {analytics && (

          <div className="grid gap-4 md:grid-cols-4 mb-8">

            <MetricCard
              title="Evidence Coverage"
              value={`${analytics.overview.coverage}%`}
            />

            <MetricCard
              title="Protection"
              value={`${analytics.overview.protection}%`}
            />

            <MetricCard
              title="Reliability"
              value={`${analytics.overview.reliability}%`}
            />

            <MetricCard
              title="Quality Score"
              value={analytics.overview.quality_score}
            />

          </div>

        )}

        {analytics && (

          <div className="grid gap-4 md:grid-cols-3 mb-8">

            <MetricCard
              title="Fingerprinted"
              value={analytics.protection.fingerprinted}
            />

            <MetricCard
              title="Hash Protected"
              value={analytics.protection.hash_protected}
            />

            <MetricCard
              title="Unprotected"
              value={analytics.protection.unprotected}
            />

          </div>

        )}

        <div className="rounded-2xl border bg-white p-8 mb-8">

          <h2 className="text-3xl font-semibold">
            Workspace Claim Registry
          </h2>

          <p className="mt-2 text-slate-500">
            Select a claim to launch investigation.
          </p>

          <div
            className="
              mt-6
              space-y-3
              max-h-[500px]
              overflow-y-auto
            "
          >

            {workspaceGraph?.nodes
              .filter(
                n => n.type === "CLAIM"
              )
              .map(claim => (

                <div
                  key={claim.id}
                  onClick={async () => {

                      const claimGraph =
                        await getEvidenceGraph(
                            workspaceId,
                            Number(claim.claim_id)
                        );

                      setGraph(
                          claimGraph as EvidenceGraphResponse
                      );

                      setSelectedClaim(claim);

                      setGraphMode(
                          "FULL INVESTIGATION"
                      );

                      setGraphStatus(
                          "Investigation initialized."
                      );

                      setSelectedNode(claim);

                      traceNodePath(claim.id);

                  }}
                  className={`
                    rounded-xl
                    border
                    p-4
                    cursor-pointer
                    hover:bg-slate-50
                    ${
                      selectedClaim?.id === claim.id
                        ? "border-blue-500 bg-blue-50"
                        : ""
                    }
                  `}
                >

                  <div className="flex justify-between">

                    <div>

                      <div className="font-semibold">
                        {claim.label}
                      </div>

                      <div className="text-sm text-slate-500">
                        {claim.id}
                      </div>

                      <div className="mt-2 text-xs text-slate-500">
                        Type: {claim.type}
                      </div>

                      <div className="text-xs text-slate-500">
                        Relationships: {
                          (workspaceGraph?.edges ?? []).filter(
                            edge =>
                              edge.source === claim.id ||
                              edge.target === claim.id
                          ).length
                        }
                      </div>

                    </div>

                    <div className="text-right">

                      <div className="text-sm font-medium">
                        CLAIM
                      </div>

                      <div className="text-xs text-slate-500">

                        {
                          (workspaceGraph?.edges ?? []).filter(
                            edge =>
                              edge.source === claim.id ||
                              edge.target === claim.id
                          ).length
                        }

                        {" "}
                        relationships

                      </div>

                    </div>

                  </div>

                </div>

              ))}

          </div>

        </div>

        {selectedClaim && (

          <div className="mt-4 rounded-xl border bg-blue-50 p-4">

            <div className="text-xs uppercase text-blue-600">
              Selected Claim
            </div>

            <div className="font-semibold">
              {selectedClaim.label}
            </div>

          </div>

        )}

        {selectedNode && (

            <InspectorPanel

                node={selectedNode}

                graph={graph}

                analytics={analytics}

                graphPath={graphPath}

                focusedNodes={focusedNodes}

                upstreamEdges={upstreamEdges}

                downstreamEdges={downstreamEdges}

                selectedNodeEdges={selectedNodeEdges}

                graphDensity={graphDensity}

                relationshipTypes={relationshipTypes}

                onClose={() => {

                    setSelectedNode(null);

                }}

            />

        )}

        <div className="rounded-2xl border bg-white p-8 mb-8">

          <h2 className="text-3xl font-semibold">
            Investigation Canvas
          </h2>

          <p className="mt-2 text-slate-500">
            Interactive institutional
            evidence network.
          </p>

        {selectedClaim && (

            <div className="mb-4 rounded-xl border bg-slate-50 p-4">

              <div className="flex items-start justify-between">

                  <div>

                      <div className="text-xs uppercase text-slate-500">
                          ACTIVE INVESTIGATION
                      </div>

                      <div className="font-semibold text-lg">
                          {selectedClaim.label}
                      </div>

                      <div className="text-sm text-slate-500">
                          {focusedNodes.length} nodes • {graphPath.length} relationships
                      </div>

                  </div>

                  <div className="text-right">

                      <div
                          className="
                              rounded-lg
                              bg-slate-900
                              px-4
                              py-2
                              text-white
                              text-sm
                              font-semibold
                          "
                      >
                          {graphMode}
                      </div>

                      <div className="mt-2 text-xs text-slate-500">
                          {graphStatus}
                      </div>

                  </div>

              </div>

            </div>

          )}

          <div
              className="mt-6"
              style={{
                  height:900,
              }}
          >

              {!selectedClaim ? (

                  <div
                      className="
                          flex
                          h-full
                          items-center
                          justify-center
                          rounded-xl
                          border
                      "
                  >

                      <div className="text-center">

                          <div className="text-2xl font-semibold">
                              Select A Claim
                          </div>

                          <div className="mt-2 text-slate-500">
                              Choose a claim from the registry
                              to begin investigation.
                          </div>

                      </div>

                  </div>

              ) : (

                  <InvestigationCanvas

                      graph={graph}

                      selectedClaimId={selectedClaim.id}

                      selectedNodeId={selectedNode?.id}

                      onNodeSelect={(nodeId: string) => {

                          const node =
                              graph.nodes.find(
                                  n => n.id === nodeId
                              );

                          if (node) {

                              setSelectedNode(node);

                              traceNodePath(node.id);

                          }

                      }}

                      onCriticalPath={async () => {

                          if (!selectedClaim?.claim_id) return;

                          setGraphStatus(
                              "Loading critical investigation path..."
                          );

                          try {

                              const g =
                                  await getCriticalPath(
                                      selectedClaim.claim_id
                                  );

                              setGraph(
                                  g as EvidenceGraphResponse
                              );

                              setGraphMode(
                                  "CRITICAL PATH"
                              );

                              setGraphStatus(
                                  "Critical investigation path loaded."
                              );

                          }

                          catch {

                              setGraphStatus(
                                  "Unable to load critical path."
                              );

                          }

                      }}

                      onRiskOnly={async () => {

                          if (!selectedClaim?.claim_id) return;

                          setGraphStatus(
                              "Loading risk graph..."
                          );

                          try {

                              const g =
                                  await getRiskGraph(
                                      selectedClaim.claim_id
                                  );

                              setGraph(
                                  g as EvidenceGraphResponse
                              );

                              setGraphMode(
                                  "RISK ANALYSIS"
                              );

                              setGraphStatus(
                                  "Risk investigation loaded."
                              );

                          }

                          catch {

                              setGraphStatus(
                                  "Unable to load risk graph."
                              );

                          }

                      }}

                      onExpand={async () => {

                          if (!selectedClaim?.claim_id) return;

                          setGraphStatus(
                              "Loading full evidence graph..."
                          );

                          try {

                              const g =
                                  await getEvidenceGraph(

                                      workspaceId,

                                      selectedClaim.claim_id

                                  );

                              setGraph(
                                  g as EvidenceGraphResponse
                              );

                              setGraphMode(
                                  "FULL GRAPH"
                              );

                              setGraphStatus(
                                  "Complete investigation graph loaded."
                              );

                          }

                          catch {

                              setGraphStatus(
                                  "Unable to expand graph."
                              );

                          }

                      }}

                      onCollapse={async () => {

                          if (!selectedClaim?.claim_id) return;

                          setGraphStatus(
                              "Collapsing investigation graph..."
                          );

                          try {

                              const g =
                                  await getFullGraph(
                                      selectedClaim.claim_id
                                  );

                              setGraph(
                                  g as EvidenceGraphResponse
                              );

                              setGraphMode(
                                  "COLLAPSED GRAPH"
                              );

                              setGraphStatus(
                                  "Collapsed investigation loaded."
                              );

                          }

                          catch {

                              setGraphStatus(
                                  "Unable to collapse graph."
                              );

                          }

                      }}

                  />

              )}

          </div>

        </div>

        {analytics &&
         analytics.exceptions.length > 0 && (

           <div className="rounded-2xl border bg-white p-8 mb-8">

             <h2 className="text-2xl font-semibold">
               Evidence Exceptions
             </h2>

             <p className="mt-2 text-slate-500">
               Missing evidence, fingerprints,
               hashes and protection failures.
             </p>

             <div
               className="
                 mt-6
                 space-y-3
                 max-h-[500px]
                 overflow-y-auto
               "
             >

               {analytics.exceptions
                 .slice(
                   0,
                   visibleNodes
                 )
                 .map(
                 (item, index) => (

                   <div
                     key={index}
                     className="rounded-xl border p-4"
                   >

                     <div className="font-semibold">
                       Trade #{item.trade_id}
                     </div>

                     <div className="text-slate-500">
                       {item.symbol}
                     </div>

                     <div className="mt-2 text-sm text-red-600">
                       {item.issues.join(", ")}
                     </div>

                   </div>

                 )
               )}

             </div>

             {analytics.exceptions.length >
                visibleNodes && (

                <div className="mt-4">

                  <button
                    onClick={() =>
                      setVisibleNodes(
                        previous =>
                          previous + 25
                      )
                    }
                    className="
                      rounded-xl
                      border
                      px-4
                      py-2
                    "
                  >
                    Load More Exceptions
                  </button>

                </div>

              )}

           </div>

         )}

        <div className="rounded-2xl border bg-white p-8 mt-8">

          <h2 className="text-3xl font-semibold">
            Evidence Infrastructure
          </h2>

          <p className="mt-2 text-slate-500">
            Institutional evidence architecture
            roadmap and subsystem readiness.
          </p>

          <div className="mt-6 grid gap-4 md:grid-cols-2">

            <InfrastructureCard
              name="Evidence Registry"
              status="ACTIVE"
            />

            <InfrastructureCard
              name="Evidence Analytics"
              status="ACTIVE"
            />

            <InfrastructureCard
              name="Evidence Graph"
              status="ACTIVE"
            />

            <InfrastructureCard
              name="Document Vault"
              status="PLANNED"
            />

            <InfrastructureCard
              name="Statement Verification"
              status="PLANNED"
            />

            <InfrastructureCard
              name="Evidence Immutability"
              status="PLANNED"
            />

            <InfrastructureCard
              name="Chain Of Custody"
              status="PLANNED"
            />

            <InfrastructureCard
              name="Evidence Provenance"
              status="PLANNED"
            />

          </div>

        </div>

      </div>

    </div>
  );
}

function MetricCard({
  title,
  value,
}: {
  title: string;
  value: string | number;
}) {

  return (

    <div className="rounded-2xl border bg-white p-6">

      <div className="text-sm text-slate-500">
        {title}
      </div>

      <div className="mt-2 text-4xl font-bold">
        {value}
      </div>

    </div>

  );

}

function InfrastructureCard({
  name,
  status,
}: {
  name: string;
  status: string;
}) {

  return (

    <div className="rounded-xl border p-4">

      <div className="font-semibold">
        {name}
      </div>

      <div className="mt-2 text-sm text-slate-500">
        {status}
      </div>

    </div>

  );

}
