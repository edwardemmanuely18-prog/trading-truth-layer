"use client";

import { useEffect, useState } from "react";
import {
  useParams,
  useSearchParams,
} from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {
  getExternalReviews,
  getExternalReviewAnalytics,
  createExternalReview,
  ExternalReview,
  ExternalReviewAnalytics,
} from "../../../../lib/api";

export default function ExternalReviewsPage() {
  const params = useParams();

  const searchParams =
    useSearchParams();

  const queryClaim =
    searchParams.get("claim");

  const [claimId, setClaimId] =
    useState(queryClaim || "");

  const workspaceId = Number(
    params.workspaceId
  );

  const [reviews, setReviews] =
    useState<ExternalReview[]>([]);

  const [analytics, setAnalytics] =
    useState<ExternalReviewAnalytics | null>(
      null
    );

  const [loading, setLoading] =
    useState(true);

  const [
    visibleReviews,
    setVisibleReviews
  ] = useState(10);

  const [reviewerName, setReviewerName] =
    useState("");

  const [
    reviewerOrganization,
    setReviewerOrganization,
  ] = useState("");

  const [reviewerRole, setReviewerRole] =
    useState("Allocator");

  const [
    observationType,
    setObservationType,
  ] = useState("Verification");

  const [
    reviewFinding,
    setReviewFinding
  ] = useState(
    "MINOR_CONCERN"
  );

  const [statement, setStatement] =
    useState("");

  const [submitting, setSubmitting] =
    useState(false);

  useEffect(() => {
    async function load() {
      try {
        const reviewData =
          await getExternalReviews(
            workspaceId
          );

        const analyticsData =
          await getExternalReviewAnalytics(
            workspaceId
          );

        setReviews(
          reviewData.reviews || []
        );

        setAnalytics(
          analyticsData
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

  async function submitReview() {
    try {
      setSubmitting(true);

      if (!claimId.trim()) {
        alert(
          "Review submission requires a target claim."
        );
        return;
      }

      if (!reviewerName.trim()) {
        alert(
          "Reviewer name is required."
        );
        return;
      }

      if (!statement.trim()) {
        alert(
          "Review statement is required."
        );
        return;
      }

      await createExternalReview(
        workspaceId,
        {
          claim_schema_id:
            Number(claimId),

          reviewer_name:
            reviewerName,

          reviewer_organization:
            reviewerOrganization,

          reviewer_role:
            reviewerRole,

          observation_type:
            observationType,

          statement,

          review_finding:
            reviewFinding,
        }
      );

      window.location.reload();

    } catch (err) {
      console.error(err);

      alert(
        "Failed to submit review."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-10">

        <div className="mb-8">

          <div className="text-xs uppercase tracking-[0.2em] text-slate-500">
            PUBLIC TRUST LAYER
          </div>

          <h1 className="mt-2 text-5xl font-bold">
            External Reviews
          </h1>

          <p className="mt-4 max-w-4xl text-slate-600">
            Independent review infrastructure
            for allocators, auditors,
            verification specialists,
            governance reviewers,
            risk officers and external
            due-diligence participants.
          </p>

        </div>

        {loading && (
          <div className="rounded-2xl border bg-white p-6">
            Loading review infrastructure...
          </div>
        )}

        {!loading && analytics && (
          <>
            <div className="grid gap-4 md:grid-cols-4 mb-8">

              <div className="rounded-2xl border bg-white p-6">
                <div className="text-sm text-slate-500">
                  Total Reviews
                </div>

                <div className="mt-2 text-4xl font-bold">
                  {analytics.total_reviews}
                </div>
              </div>

              <div className="rounded-2xl border bg-white p-6">
                <div className="text-sm text-slate-500">
                  Reviewer Roles
                </div>

                <div className="mt-2 text-4xl font-bold">
                  {
                    Object.keys(
                      analytics.roles
                    ).length
                  }
                </div>
              </div>

              <div className="rounded-2xl border bg-white p-6">
                <div className="text-sm text-slate-500">
                  Observation Types
                </div>

                <div className="mt-2 text-4xl font-bold">
                  {
                    Object.keys(
                      analytics.observation_types
                    ).length
                  }
                </div>
              </div>

              <div className="rounded-2xl border bg-white p-6">
                <div className="text-sm text-slate-500">
                  Registry Status
                </div>

                <div className="mt-2 text-xl font-semibold text-emerald-600">
                  Active
                </div>
              </div>

            </div>

            <div className="rounded-2xl border bg-white p-8 mb-8">

              <div className="text-xs uppercase tracking-[0.2em] text-slate-500">
                REVIEW INFRASTRUCTURE
              </div>

              <h2 className="mt-3 text-3xl font-semibold">
                Institutional Review Registry
              </h2>

              <p className="mt-4 text-slate-600">
                Review statements become part
                of the trust layer surrounding
                publicly verifiable claims.
                These records support allocator
                due diligence, audit workflows,
                governance oversight and
                verification review.
              </p>

            </div>

            <div className="rounded-2xl border bg-white p-8 mb-8">

              <div className="text-xs uppercase tracking-[0.2em] text-slate-500">
                REVIEW SUBMISSION
              </div>

              <div className="mt-4 rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">

                Reviews may only target
                VERIFIED, PUBLISHED or
                LOCKED claims.

                Review classification,
                rating assignment,
                trust impact and risk
                scoring are determined
                automatically by the
                platform.

              </div>

              <h2 className="mt-3 text-3xl font-semibold">
                Submit Institutional Review
              </h2>

              <p className="mt-4 text-slate-600">
                Review statements become part
                of the public trust layer and
                support allocator due diligence,
                governance review and verification.
              </p>

              <div className="mt-8 grid gap-4 md:grid-cols-2">

                <div>
                  <label className="mb-2 block text-sm font-medium">
                    Reviewer Name
                  </label>

                  <input
                    value={reviewerName}
                    onChange={(e) =>
                      setReviewerName(e.target.value)
                    }
                    placeholder="Reviewer Name"
                    className="w-full rounded-xl border p-3"
                  />
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium">
                    Organization
                  </label>

                  <input
                    value={reviewerOrganization}
                    onChange={(e) =>
                      setReviewerOrganization(
                        e.target.value
                      )
                    }
                    placeholder="Organization"
                    className="w-full rounded-xl border p-3"
                  />
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium">
                    Reviewer Role
                  </label>

                  <select
                    value={reviewerRole}
                    onChange={(e) =>
                      setReviewerRole(e.target.value)
                    }
                    className="w-full rounded-xl border p-3"
                  >
                    <option>Allocator</option>
                    <option>Auditor</option>
                    <option>Risk Officer</option>
                    <option>Verification Specialist</option>
                    <option>Governance Reviewer</option>
                    <option>Research Analyst</option>
                  </select>
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium">
                    Observation Type
                  </label>

                  <select
                    value={observationType}
                    onChange={(e) =>
                      setObservationType(
                        e.target.value
                      )
                    }
                    className="w-full rounded-xl border p-3"
                  >
                    <option>Verification</option>
                    <option>Risk</option>
                    <option>Performance</option>
                    <option>Governance</option>
                    <option>Integrity</option>
                    <option>Evidence</option>
                    <option>Allocation</option>
                  </select>
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium">
                    Review Finding
                  </label>

                  <select
                    value={reviewFinding}
                    onChange={(e) =>
                      setReviewFinding(
                        e.target.value
                      )
                    }
                    className="w-full rounded-xl border p-3"
                  >
                    <option value="VERIFIED">
                      Verified
                    </option>

                    <option value="MINOR_CONCERN">
                      Minor Concern
                    </option>

                    <option value="MATERIAL_CONCERN">
                      Material Concern
                    </option>

                    <option value="CRITICAL_FINDING">
                      Critical Finding
                    </option>
                  </select>
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium">
                    Target Verified Claim
                  </label>

                  <input
                    value={claimId}
                    onChange={(e) =>
                      setClaimId(e.target.value)
                    }
                    placeholder="Enter verified, published or locked claim ID"
                    className="w-full rounded-xl border p-3"
                  />
                </div>

              </div>

              <div className="mt-6">

                <label className="mb-2 block text-sm font-medium">
                  Review Statement
                </label>

                <textarea
                  placeholder="Review statement, due diligence findings, audit observations, governance concerns, verification comments..."
                  value={statement}
                  onChange={(e) =>
                    setStatement(
                      e.target.value
                    )
                  }
                  className="min-h-[220px] w-full rounded-xl border p-4"
                />

                <button
                  onClick={submitReview}
                  disabled={submitting}
                  className="mt-4 rounded-xl bg-slate-900 px-6 py-3 text-white disabled:opacity-50"
                >
                  {submitting
                    ? "Submitting..."
                    : "Submit Review"}
                </button>

              </div>
            </div>


            {reviews.length === 0 && (

              <div className="rounded-2xl border bg-white p-10">

                <h3 className="text-2xl font-semibold">
                  No Review Statements
                </h3>

                <p className="mt-4 text-slate-600">
                  No external review statements
                  have been submitted for this
                  workspace.
                </p>

              </div>

            )}

            <div
              className="
                space-y-6
                max-h-[1200px]
                overflow-y-auto
                pr-2
              "
            >

              {reviews
                .slice(0, visibleReviews)
                .map((review) => (

                <div
                  key={review.id}
                  className="rounded-2xl border bg-white p-8"
                >

                  <div className="flex flex-wrap gap-2 mb-4">

                    <span className="rounded-full border border-emerald-300 bg-emerald-50 px-3 py-1 text-sm text-emerald-700">
                      {review.reviewer_role}
                    </span>

                    <span className="rounded-full border border-blue-300 bg-blue-50 px-3 py-1 text-sm text-blue-700">
                      {review.observation_type}
                    </span>

                    <span
                      className={
                        review.review_direction === "POSITIVE"
                          ? "rounded-full border border-emerald-300 bg-emerald-50 px-3 py-1 text-sm text-emerald-700"
                          : review.review_direction === "NEGATIVE"
                          ? "rounded-full border border-amber-300 bg-amber-50 px-3 py-1 text-sm text-amber-700"
                          : review.review_direction === "CRITICAL"
                          ? "rounded-full border border-red-300 bg-red-50 px-3 py-1 text-sm text-red-700"
                          : "rounded-full border border-slate-300 bg-slate-50 px-3 py-1 text-sm text-slate-700"
                      }
                    >
                      {review.review_direction}
                    </span>

                  </div>

                  <h3 className="text-2xl font-semibold">
                    {review.reviewer_name}
                  </h3>

                  <div className="mt-2 text-slate-500">
                    {review.reviewer_organization ||
                      "Independent Reviewer"}
                  </div>

                  <div className="mt-6 rounded-xl border p-5">
                    {review.statement}
                  </div>

                  <div className="mt-6 grid gap-4 md:grid-cols-4">

                    <div className="rounded-xl border p-4">
                      <div className="text-xs text-slate-500">
                        CLAIM
                      </div>

                      <div className="mt-2 font-semibold">
                        {review.claim_schema_id}
                      </div>
                    </div>

                    <div className="rounded-xl border p-4">
                      <div className="text-xs text-slate-500">
                        STATUS
                      </div>

                      <div className="mt-2 font-semibold">
                        {review.status}
                      </div>
                    </div>

                    <div className="rounded-xl border p-4">
                      <div className="text-xs text-slate-500">
                        RATING
                      </div>

                      <div className="mt-2 font-semibold">
                        {review.rating ?? "N/A"}
                      </div>
                    </div>

                    <div className="rounded-xl border p-4">
                      <div className="text-xs text-slate-500">
                        CREATED
                      </div>

                      <div className="mt-2 font-semibold">
                        {review.created_at ??
                          "—"}
                      </div>
                    </div>

                  </div>

                </div>

              ))}

              {reviews.length >
                visibleReviews && (

                <div className="mt-8 flex justify-center">

                  <button
                    onClick={() =>
                      setVisibleReviews(
                        visibleReviews + 10
                      )
                    }
                    className="rounded-xl bg-slate-900 px-6 py-3 text-white"
                  >
                    Load More Reviews
                  </button>

                </div>

              )}

            </div>
          </>
        )}

      </div>
    </div>
  );
}